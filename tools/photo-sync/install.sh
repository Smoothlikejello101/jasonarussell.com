#!/usr/bin/env bash
# Installs photo-sync for the current user:
#   - dependencies (Pillow, exiftool, rclone)
#   - the photo-sync command in ~/.local/bin
#   - a connection to the R2 bucket (asks for an R2 API token once)
#   - a systemd user timer that checks the watch folder every 2 minutes
#
# Usage: bash install.sh [WATCH_FOLDER]
# Default watch folder: ~/Pictures/Photos/Export/Website
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
WATCH_DIR="${1:-$HOME/Pictures/Photos/Export/Website}"
BUCKET="jasonarussell-photos"
REMOTE="r2"

say() { printf '\n\033[1m%s\033[0m\n' "$*"; }

say "1/5  Installing dependencies (asks for your password)"
sudo apt-get update -qq
sudo apt-get install -y -qq python3-pil libimage-exiftool-perl rclone

say "2/5  Installing the photo-sync command"
mkdir -p "$HOME/.local/bin" "$HOME/.config/photo-sync" "$HOME/.config/systemd/user" "$HOME/.local/state/photo-sync"
install -m 755 "$HERE/photo_sync.py" "$HOME/.local/bin/photo-sync"

say "3/5  Watch folder: $WATCH_DIR"
mkdir -p "$WATCH_DIR"
if [ ! -f "$HOME/.config/photo-sync/config.ini" ]; then
  cat > "$HOME/.config/photo-sync/config.ini" <<EOF
[photo-sync]
# Folder darktable exports website photos into (full size is fine).
watch_dir = $WATCH_DIR
# Also look in subfolders?
recursive = false
remote = $REMOTE
bucket = $BUCKET
EOF
else
  echo "Keeping existing config at ~/.config/photo-sync/config.ini"
fi

say "4/5  Connecting to Cloudflare R2"
if rclone listremotes | grep -qx "${REMOTE}:"; then
  echo "rclone remote '$REMOTE' already exists; keeping it."
else
  echo "In the Cloudflare dashboard: R2 → Manage API tokens → Create API token."
  echo "Permission: Object Read & Write. Scope it to the bucket '$BUCKET'."
  echo "Then copy the three values it shows you."
  read -rp  "  Account ID (the part before .r2.cloudflarestorage.com): " ACCOUNT_ID
  read -rp  "  Access Key ID: " ACCESS_KEY
  read -rsp "  Secret Access Key (hidden): " SECRET_KEY; echo
  # Older rclone (before 1.58) has no 'Cloudflare' provider; 'Other' works the same for R2.
  PROVIDER=Cloudflare
  RV=$(rclone version | head -1 | sed -E 's/.*v([0-9]+)\.([0-9]+).*/\1 \2/')
  set -- $RV; if [ "${1:-1}" -eq 1 ] && [ "${2:-99}" -lt 58 ]; then PROVIDER=Other; fi
  rclone config create "$REMOTE" s3 provider="$PROVIDER" \
    access_key_id="$ACCESS_KEY" secret_access_key="$SECRET_KEY" \
    endpoint="https://${ACCOUNT_ID}.r2.cloudflarestorage.com" region=auto \
    acl=private no_check_bucket=true >/dev/null
fi
if rclone lsf "${REMOTE}:${BUCKET}" >/dev/null 2>&1; then
  echo "Connected to the '$BUCKET' bucket."
else
  echo "Couldn't reach the bucket. Check the token values, then run:  rclone config delete $REMOTE  and re-run this installer."
  exit 1
fi

say "5/5  Starting the background timer"
cat > "$HOME/.config/systemd/user/photo-sync.service" <<'EOF'
[Unit]
Description=Upload web-sized copies of new photo exports to jasonarussell.com

[Service]
Type=oneshot
ExecStart=%h/.local/bin/photo-sync
Nice=10
EOF
cat > "$HOME/.config/systemd/user/photo-sync.timer" <<'EOF'
[Unit]
Description=Check for new photo exports every 2 minutes

[Timer]
OnBootSec=2min
OnUnitActiveSec=2min
Persistent=true

[Install]
WantedBy=timers.target
EOF
systemctl --user daemon-reload
systemctl --user enable --now photo-sync.timer

say "Done."
COUNT=$(find "$WATCH_DIR" -maxdepth 1 -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.tif' -o -iname '*.tiff' \) | wc -l)
echo "Photos already in the watch folder: $COUNT (they'll upload within a couple of minutes)."
echo "Watch it work:   journalctl --user -u photo-sync -f"
echo "What's uploaded: photo-sync --status"
