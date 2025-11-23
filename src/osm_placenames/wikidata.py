#!/usr/bin/env python3
import csv
import time
import traceback
from pathlib import Path
from typing import Annotated

import typer
from rich.progress import BarColumn, MofNCompleteColumn, Progress, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from wikidata import __version__ as wikidata_version
from wikidata.client import Client
from wikidata.entity import EntityId

from osm_placenames import __version__ as osm_places_version

app = typer.Typer()


def get_wikidata(wdid: str, client: Client) -> dict[str, str]:
    e = client.get(EntityId(wdid), load=True)
    time.sleep(0.1)
    attr = e.attributes
    desc = attr.get("descriptions", {}).get("en", {}).get("value")  # ty: ignore[unresolved-attribute]
    if desc is not None:
        desc = desc[0].upper() + desc[1:]
    return {
        "description": desc,
        "wikipedia": attr.get("sitelinks", {}).get("enwiki", {}).get("url"),  # ty: ignore[unresolved-attribute]
    }


@app.command()
def main(
    inputfile: Annotated[Path, typer.Argument(exists=True, dir_okay=False, file_okay=True, readable=True)],
    outputfile: Annotated[Path, typer.Argument(dir_okay=False, file_okay=True, writable=True)],
) -> None:
    """
    Read an input CSV file and enrich it with info from Wikidata

    In particular, lookup the Wikidata object found in the column 'wikidata'

    From this page, the object 'description' and link to English Wikipedia is added to the output CSV file under the
    columns 'wikipedia' and 'description'.
    """
    client = Client(
        user_agent=f"osm-placenames-wikidata-resolver/{osm_places_version} (https://github.com/rasher/osm-placenames) "
        f"Wikidata/{wikidata_version}"
    )

    places = []
    fields = []
    with open(inputfile) as infp:
        reader = csv.DictReader(infp)
        places = list(reader)
        fields = list(reader.fieldnames) if reader.fieldnames else []

    progress_bar = Progress(
        TextColumn("Fetching Wikidata [progress.percentage]{task.percentage:>3.0f}%"),
        BarColumn(),
        MofNCompleteColumn(),
        TextColumn("•"),
        TimeElapsedColumn(),
        TextColumn("•"),
        TimeRemainingColumn(),
    )

    fields.append("description")
    with open(outputfile, "w") as outfp:
        writer = csv.DictWriter(outfp, fields)
        writer.writeheader()
        with progress_bar as p:
            for place in p.track(places):
                wd = place.get("wikidata")
                if wd:
                    try:
                        wikidata = get_wikidata(place.get("wikidata"), client)
                        place.update(wikidata)
                    except Exception:
                        traceback.print_exc()
                writer.writerow(place)


if __name__ == "__main__":
    app()
