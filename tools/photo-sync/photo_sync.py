#!/usr/bin/env python3
"""
photo-sync: make web-sized copies of new darktable exports and upload them to R2.

Runs every couple of minutes from a systemd user timer (see install.sh). Each run:
  1. Scans the watch folder for new or changed exports (JPEG, PNG, 8-bit TIFF).
  2. For each, writes a copy at most 4000px on the long edge, under 19 MB, keeping
     the color profile and the darktable title, description, and rating, but no
     camera EXIF or GPS location.
  3. Uploads the copy to the R2 bucket with rclone, under the same name (.jpg).

Your full-size exports never leave this computer.

Usage:
  photo-sync              process anything new, then exit (what the timer runs)
  photo-sync --dry-run    show what would be processed, change nothing
  photo-sync --redo NAME  force one file to be reprocessed and re-uploaded
  photo-sync --status     list what has been uploaded
"""
import argparse
import configparser
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageFile, ImageOps

Image.MAX_IMAGE_PIXELS = 250_000_000  # allow big stitched/stacked files
ImageFile.MAXBLOCK = 64 * 1024 * 1024  # room for optimized progressive JPEGs

HOME = Path.home()
CONFIG = HOME / ".config/photo-sync/config.ini"
STATE_DIR = HOME / ".local/state/photo-sync"
WEB_DIR = STATE_DIR / "web"
STATE_FILE = STATE_DIR / "state.json"

EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
LONG_EDGE = 4000
QUALITY = 92
MAX_BYTES = 19 * 1024 * 1024  # Cloudflare's limit is 20 MB; stay under it

# Metadata carried over to the web copy. Everything else (camera EXIF, GPS) is dropped.
KEEP_TAGS = [
    "-XMP-dc:Title", "-XMP-dc:Description", "-XMP-dc:Creator", "-XMP-dc:Rights",
    "-XMP-xmp:Rating", "-IFD0:Artist", "-IFD0:Copyright",
]


def log(*parts):
    print(time.strftime("%Y-%m-%d %H:%M:%S"), *parts, flush=True)


def load_config():
    cfg = configparser.ConfigParser()
    if not cfg.read(CONFIG):
        sys.exit(f"No config at {CONFIG}. Run install.sh first.")
    s = cfg["photo-sync"]
    return {
        "watch_dir": Path(os.path.expanduser(s.get("watch_dir"))),
        "remote": s.get("remote", "r2"),
        "bucket": s.get("bucket", "jasonarussell-photos"),
        "recursive": s.getboolean("recursive", fallback=False),
    }


def load_state():
    try:
        return json.loads(STATE_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_state(state):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=1, sort_keys=True))
    tmp.replace(STATE_FILE)


def candidates(watch_dir, recursive):
    it = watch_dir.rglob("*") if recursive else watch_dir.iterdir()
    for p in sorted(it):
        if p.is_file() and p.suffix.lower() in EXTS and not p.name.startswith("."):
            yield p


def is_settled(p, wait=2.0):
    """True if the file isn't still being written."""
    a = p.stat()
    if time.time() - a.st_mtime > 10:
        return True
    time.sleep(wait)
    b = p.stat()
    return a.st_size == b.st_size and a.st_mtime == b.st_mtime


def web_name(src):
    return src.stem + ".jpg"


def make_web_copy(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix(".tmp.jpg")
    with Image.open(src) as im:
        icc = im.info.get("icc_profile")
        im = ImageOps.exif_transpose(im)
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        im.thumbnail((LONG_EDGE, LONG_EDGE), Image.LANCZOS)
        q = QUALITY
        while True:
            im.save(tmp, "JPEG", quality=q, optimize=True, progressive=True,
                    subsampling=0 if q >= 90 else 2, icc_profile=icc)
            if tmp.stat().st_size <= MAX_BYTES or q <= 70:
                break
            q -= 6
    subprocess.run(["exiftool", "-q", "-q", "-overwrite_original", "-TagsFromFile", str(src),
                    *KEEP_TAGS, str(tmp)], check=True)
    tmp.replace(dst)
    return q


def upload(cfg, local, name):
    target = f"{cfg['remote']}:{cfg['bucket']}/{name}"
    subprocess.run(["rclone", "copyto", "--retries", "3", str(local), target], check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--redo", metavar="NAME", help="reprocess this file (name as it appears in the watch folder)")
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()

    cfg = load_config()
    state = load_state()

    if args.status:
        for k, v in sorted(state.items()):
            print(f"{v.get('uploaded', '?'):19}  {k}  ->  {v.get('name')}")
        return
    if not cfg["watch_dir"].is_dir():
        sys.exit(f"Watch folder not found: {cfg['watch_dir']}")
    if args.redo:
        state = {k: v for k, v in state.items() if Path(k).name != args.redo}

    done = 0
    for src in candidates(cfg["watch_dir"], cfg["recursive"]):
        key = str(src.relative_to(cfg["watch_dir"]))
        st = src.stat()
        sig = {"size": st.st_size, "mtime": int(st.st_mtime)}
        prev = state.get(key)
        if prev and prev.get("size") == sig["size"] and prev.get("mtime") == sig["mtime"]:
            continue
        if args.dry_run:
            log("would upload", key, "->", web_name(src))
            continue
        if not is_settled(src):
            log("still being written, will retry:", key)
            continue
        try:
            out = WEB_DIR / web_name(src)
            q = make_web_copy(src, out)
            upload(cfg, out, out.name)
            state[key] = {**sig, "name": out.name, "quality": q,
                          "bytes": out.stat().st_size,
                          "uploaded": time.strftime("%Y-%m-%d %H:%M:%S")}
            save_state(state)
            done += 1
            log(f"uploaded {out.name} ({out.stat().st_size / 1048576:.1f} MB, quality {q}) from {key}")
        except Exception as e:  # keep going; this file is retried next run
            log("FAILED", key, "-", e)
    if done:
        log(f"{done} photo(s) uploaded. They appear on the site within about 10 minutes.")


if __name__ == "__main__":
    main()
