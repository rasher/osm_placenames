# OSM Placenames

OSM Placenames creates list of placenames from OSM and Wikidata

* Free software: MIT License

## Features

The package contains three tools

* `osm-placenames`: Extract 'place' objects from an [OpenStreetMap](https://openstreetmap.org/) database dump in pbf
  format and write to a CSV file.
* `resolve-wikidata`: Reads a CSV file and looks up data from [WikiData](https://wikidata.org), adding description
  and link to English Wikipedia.
* `db-format`: Read CSV file and output in specific format with various modification.

For each tool, see `cmd --help` for more detail and usage instructions.

## Credits

This package was created with [Cookiecutter](https://github.com/audreyfeldroy/cookiecutter) and the [audreyfeldroy/cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage) project template.
