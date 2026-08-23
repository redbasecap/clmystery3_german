#!/bin/sh
# Beschlagnahmtes Server-Image des Versands wiederherstellen:
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
rm -rf "$DIR/.git"
cp -R "$DIR/.gitarchiv" "$DIR/.git"
echo "Image wiederhergestellt. Ab jetzt: cd in dieses Verzeichnis und git nutzen."
