# photo-sync

Export full-size from darktable into one folder. Within about two minutes, this tool:

1. makes a copy at most 4000px on the long edge and under 19 MB,
2. keeps the color profile and your darktable **title, description, and rating**, but drops camera EXIF and **GPS location**,
3. uploads that copy to the private R2 bucket. It appears on the site within about 10 minutes.

Your full-size exports never leave your computer.

## Install (once)

```bash
cd tools/photo-sync
bash install.sh                      # watches ~/Pictures/Photos/Export/Website
bash install.sh ~/some/other/folder  # or pick the folder
```

It installs Pillow, exiftool and rclone, asks for an R2 API token once, and starts a systemd user timer.

**R2 API token:** Cloudflare dashboard → R2 → Manage API tokens → Create API token. Use *Object Read & Write*, scoped to `jasonarussell-photos`. The installer asks for the Account ID, Access Key ID, and Secret Access Key it shows you.

## darktable

Add an export preset, for example "Website":
- Target storage: file on disk, `$(HOME)/Pictures/Photos/Export/Website/$(FILE_NAME)`
- Format: JPEG (or 8-bit TIFF), any size, including full size
- Preferences (gear) → metadata: **on** for *metadata* (title, description, rating). Geo tags can stay on; photo-sync strips them.

Anything exported to that folder goes on the site. Export elsewhere for photos you don't want published.

## Day to day

| Want to… | Do this |
| --- | --- |
| Publish a photo | Export it into the watch folder |
| Update one (new edit, new title) | Re-export with the same name; it re-uploads |
| Watch it run | `journalctl --user -u photo-sync -f` |
| See what's uploaded | `photo-sync --status` |
| Force a re-upload | `photo-sync --redo "Tulip 13754.jpg"` |
| Take a photo down | Delete it in the R2 dashboard (bucket `jasonarussell-photos`) |
| Pause syncing | `systemctl --user stop photo-sync.timer` (`start` to resume) |

Deleting a file from the watch folder does **not** remove it from the site. That's deliberate, so cleaning up your disk never unpublishes anything.

16-bit TIFFs aren't supported; export JPEG or 8-bit TIFF to this folder.
