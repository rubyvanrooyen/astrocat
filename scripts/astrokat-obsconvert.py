#!/usr/bin/env python

"""Conversion between YAML and JSON observation file formats"""

from __future__ import print_function

from astrokat import (
                      # catalogue,
                      jsontools,
                      yamltools,
                      __version__)

import argparse
import argcomplete


def main(json_file=None,
         yaml_file=None):

    print(yaml_file)
    data = yamltools.read(yaml_file)
    print(data)
    yamltools.write2json(data)


if __name__ == "__main__":

    usage = "%(prog)s [options]"
    description = ("conversion between YAML and JSON")

    parser = argparse.ArgumentParser(
        usage=usage,
        description=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--version",
                        action="version",
                        version=__version__)
    parser.add_argument("--yaml",
                        type=str,
                        help="file to convert to JSON")
    parser.add_argument("--json",
                        type=str,
                        help="file to convert to YAML")
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    main(json_file=args.json,
         yaml_file=args.yaml)

# -fin-
