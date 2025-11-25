#!/bin/sh

if [ -z "$1" ]; then
    echo "Usage: $0 https://download.geofabrik.de/europe/united-kingdom/england-latest.osm.pbf" 1>&2
    exit 1
fi

url=$1
pbf=$(basename "$url")
area=$(basename "$url" .osm.pbf|sed 's/-latest//')

wget --no-verbose --timestamping "$url"
mtime_epoch=$(stat -c %Y "$pbf")
mtime_str=$(date -d "@${mtime_epoch}" +%Y%m%dT%H%M%S)

prefix="${area}_${mtime_str}_"
places="${prefix}places.csv"
wikidata="${prefix}wikidata.csv"
dbformat="${prefix}dbformat.csv"

uv run osm-placenames "$pbf" "${places}"
uv run resolve-wikidata "${places}" "${wikidata}"
uv run db-format "${wikidata}" "${dbformat}"
