#!/usr/bin/env bash
# Rebuilds every README image. Needs python3 with Pillow and numpy, Blender, and a headless Chromium screenshot tool.
# SHOT is any command taking <url> <out.png> <WxH>; it defaults to Playwright's CLI.
set -euo pipefail
cd "$(dirname "$0")/../.."
TMP="$(mktemp -d)"
SHOT="${SHOT:-npx --yes playwright screenshot --viewport-size}"

python3 scripts/brand/make_logos.py
python3 scripts/brand/make_env.py "$TMP/studio.png"
blender -b -P scripts/brand/make_mark_3d.py -- "$TMP/mark.png" "$TMP/mark.glb" 1100 96 "$TMP/studio.png"
python3 - "$TMP/mark.png" <<'EOF'
import sys
from PIL import Image
mark = Image.open(sys.argv[1])
mark = mark.crop(mark.getbbox())
mark.thumbnail((900, 900))
mark.save("assets/janitor-3d.png")
EOF
python3 scripts/brand/make_terminal_gif.py
if [[ "$SHOT" == npx* ]]; then
  $SHOT 1280,640 "file://$PWD/scripts/brand/social.html" assets/social-preview.png
  $SHOT 2400,1000 "file://$PWD/scripts/brand/flow.html" assets/flow.png
else
  $SHOT "file://$PWD/scripts/brand/social.html" assets/social-preview.png 1280x640
  $SHOT "file://$PWD/scripts/brand/flow.html" assets/flow.png 2400x1000
fi
rm -rf "$TMP"
