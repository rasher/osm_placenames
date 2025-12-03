#!/usr/bin/env python3

import csv
from pathlib import Path
from typing import Annotated

import typer
from rich.progress import BarColumn, MofNCompleteColumn, Progress, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from shapely.geometry import MultiPolygon, Point

from .poly import parse_poly

app = typer.Typer()


def get_polys(poly_dir: Path) -> dict[str, MultiPolygon]:
    polys = {}
    for poly_file in poly_dir.glob("*.poly"):
        with open(poly_file) as f:
            polys[poly_file.stem] = parse_poly(f.readlines())
    return polys


@app.command()
def main(
    inputfile: Annotated[Path, typer.Argument(exists=True, dir_okay=False, file_okay=True, readable=True)],
    outputfile: Annotated[Path, typer.Argument(dir_okay=False, file_okay=True, writable=True)],
    polys_dir: Annotated[
        Path, typer.Argument(dir_okay=True, file_okay=False, exists=True, help="Directory containing .poly files")
    ],
):
    """
    Read an input CSV file and determine which Multipolygon each line lies in.

    Output the same CSV file, with an added column 'is_in' stating for each line which Multigon it lies in.
    """
    polys = get_polys(polys_dir)

    places = []
    fields = []
    with open(inputfile) as infp:
        reader = csv.DictReader(infp)
        places = list(reader)
        fields = list(reader.fieldnames) if reader.fieldnames else []
    fields.append("is_in")

    progress_bar = Progress(
        TextColumn("Checking locations [progress.percentage]{task.percentage:>3.0f}%"),
        BarColumn(),
        MofNCompleteColumn(),
        TextColumn("•"),
        TimeElapsedColumn(),
        TextColumn("•"),
        TimeRemainingColumn(),
    )

    with open(outputfile, "w") as out_fp:
        with progress_bar as p:
            writer = csv.DictWriter(out_fp, fields)
            writer.writeheader()
            for place in p.track(places):
                p = Point(place["lon"], place["lat"])
                is_in = next(filter(lambda c: c[1].contains(p), polys.items()), None)
                if is_in is not None:
                    name, poly = is_in
                    place["is_in"] = name
                writer.writerow(place)


if __name__ == "__main__":
    app()
