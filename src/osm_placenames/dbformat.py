#!/usr/bin/env python3
import csv
import re
import sys
import unicodedata
import urllib.parse
from pathlib import Path
from typing import Annotated

import typer
from rich.progress import BarColumn, MofNCompleteColumn, Progress, TextColumn, TimeElapsedColumn, TimeRemainingColumn

app = typer.Typer()

# https://stackoverflow.com/a/93029
all_chars = (chr(i) for i in range(sys.maxunicode))
categories = {"Cc", "Cf"}
control_chars = "".join(c for c in all_chars if unicodedata.category(c) in categories)
CONTROL_CHAR_REGEX = re.compile(f"[{re.escape(control_chars)}]")

CLEANUP_REGEXES = [
    CONTROL_CHAR_REGEX,
    re.compile(r"\s*([,.] |(in )?(the )?)(UK|United Kingdom).*$"),
    re.compile(r"\s*([,.] |in | )England\s*$"),
    re.compile(r" (and|of)$"),
    re.compile(r" and (former |defunct )?(civil )?parish"),
    re.compile(r" and unparished area"),
    re.compile(r" and farm\b"),
]


def cleanup_description(desc: str) -> str:
    desc = desc.strip()
    if len(desc) > 0:
        desc = desc[0].upper() + desc[1:]
    for regex in CLEANUP_REGEXES:
        desc = regex.sub("", desc)
    return desc


def cleanup_wp(wp: str) -> str:
    # These should not happen, but just in case
    wp = wp.replace("+", "_")
    wp = wp.replace(" ", "_")
    # percent-encode the path, but keep / and % (for any already-encoded urls)
    parsed = urllib.parse.urlparse(wp)
    return parsed._replace(path=urllib.parse.quote(parsed.path, safe="/%_")).geturl()


@app.command()
def main(
    inputfile: Annotated[Path, typer.Argument(exists=True, dir_okay=False, file_okay=True, readable=True)],
    outputfile: Annotated[Path, typer.Argument(exists=False, dir_okay=False, file_okay=True, writable=True)],
) -> None:
    """
    Read CSV file with columns 'name', 'wikipedia' and 'description' and output a version of these with escaped URLs,
    simplified descriptions (removing references to England and UK) using the headers 'settlementLabel', 'wikiLink' and
    'description'.
    """
    places = []
    with open(inputfile) as infp:
        reader = csv.DictReader(infp)
        places = list(sorted(reader, key=lambda p: (p.get("name"), float(p.get("lon")))))

    progress_bar = Progress(
        TextColumn("Converting data [progress.percentage]{task.percentage:>3.0f}%"),
        BarColumn(),
        MofNCompleteColumn(),
        TextColumn("•"),
        TimeElapsedColumn(),
        TextColumn("•"),
        TimeRemainingColumn(),
    )

    with open(outputfile, "w") as outfp:
        fields = ["settlementLabel", "wikiLink", "description"]
        writer = csv.DictWriter(outfp, fields)
        writer.writeheader()
        wps = set()
        with progress_bar as p:
            for place in p.track(places):
                wp = place.get("wikipedia")
                desc = place.get("description")
                if desc is not None:
                    desc = cleanup_description(desc)
                if wp:
                    wp = cleanup_wp(wp)
                    if wp in wps:
                        continue
                    wps.add(wp)
                    writer.writerow(
                        {
                            "settlementLabel": place["name"],
                            "wikiLink": wp,
                            "description": desc,
                        }
                    )


if __name__ == "__main__":
    app()
