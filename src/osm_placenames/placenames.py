#!/usr/bin/env python3
import csv
import re
from pathlib import Path
from typing import Annotated
from urllib.parse import quote

import osmium
import typer
from osmium import filter
from osmium.osm import Area, Node, Relation, Way
from rich.progress import (
    Progress,
    SpinnerColumn,
)
from shapely.geometry import shape

DEFAULT_TAGS = ["place", "lat", "lon", "name", "wikipedia", "wikidata"]

DEFAULT_PLACE_TYPES = [
    "city",
    "town",
    "village",
    "hamlet",
    # "isolated_dwelling",  # Probably too small to include
]

app = typer.Typer()


def get_location(obj: Node | Way | Relation | Area) -> dict[str, float]:
    cnt = shape(obj.__geo_interface__["geometry"]).centroid  # ty: ignore[unresolved-attribute]
    return {"lat": cnt.y, "lon": cnt.x}


def get_wikipedia(obj: Node | Way | Relation | Area) -> dict[str, str]:
    """
    Expand Wikipedia reference (xx:Page) to URL (https://xx.wikipedia.org/wiki/Page)
    """
    wp = obj.tags.get("wikipedia")
    wp_re = re.compile(r"([a-z]+):(.*)")
    if wp is not None and (m := wp_re.match(wp)):
        lang = m.group(1)
        page = quote(m.group(2).replace(" ", "_"))
        return {"wikipedia": f"https://{lang}.wikipedia.org/wiki/{page}"}
    elif wp is not None:
        return {"wikipedia": wp}
    else:
        return {}


@app.command()
def main(
    inputfile: Annotated[
        Path, typer.Argument(exists=True, dir_okay=False, file_okay=True, readable=True, help="Input OSM pbf")
    ],
    outputfile: Annotated[Path, typer.Argument(exists=False, help="Output CSV file")],
    place_type: Annotated[
        list[str] | None,
        typer.Option(
            show_default=", ".join(DEFAULT_PLACE_TYPES),
            help="OSM place type to include in output. May be used multiple times",
            default_factory=lambda: DEFAULT_PLACE_TYPES,
        ),
    ],
    include_tag: Annotated[
        list[str] | None,
        typer.Option(
            show_default=", ".join(DEFAULT_TAGS),
            help="Tags to include in output. May be used multiple times",
            default_factory=lambda: DEFAULT_TAGS,
        ),
    ],
) -> None:
    """
    Extract place names from an OpenStreetMap pbf export and output to CSV
    """
    if place_type is None:
        place_type = DEFAULT_PLACE_TYPES
    if include_tag is None:
        include_tag = DEFAULT_TAGS

    with open(outputfile, "w") as outf:
        out_csv = csv.DictWriter(outf, include_tag, extrasaction="ignore")
        out_csv.writeheader()
        processor = (
            osmium.FileProcessor(str(inputfile))
            .with_filter(filter.KeyFilter("name"))
            .with_filter(filter.TagFilter(*[("place", v) for v in place_type]))
            .with_filter(filter.GeoInterfaceFilter())
            .with_locations()
            .with_areas()
        )

        with Progress(SpinnerColumn(), "Extracting places: {task.completed}") as p:
            for obj in p.track(processor):
                tags = {k: v for k, v in obj.tags}
                tags.update(get_location(obj))
                tags.update(get_wikipedia(obj))
                out_csv.writerow(tags)


if __name__ == "__main__":
    app()
