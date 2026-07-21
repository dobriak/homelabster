#!/bin/sh
set -eu

mkdir -p "$HOMELABSTER_DATA_DIR/icons"

for filename in services.yaml categories.yaml ipam.yaml; do
    destination="$HOMELABSTER_DATA_DIR/$filename"
    if [ ! -f "$destination" ]; then
        cp "/defaults/$filename.example" "$destination"
    fi
done

exec "$@"
