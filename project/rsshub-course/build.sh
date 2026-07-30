#!/bin/bash
# Assembles the course from parts.
# Run from the course directory: bash build.sh
set -e
cat _base.html modules/*.html _footer.html > index.html
echo "Built index.html — open it in your browser."

# Refresh the gallery so the new/updated course appears on the dashboard.
GALLERY="$(dirname "$PWD")/build-gallery.sh"
if [ -f "$GALLERY" ]; then
  (cd "$(dirname "$GALLERY")" && bash "$(basename "$GALLERY")") || echo "(gallery refresh skipped)"
fi
