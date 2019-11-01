""" Read target information from CSV catalogue file"""

from __future__ import division
from __future__ import absolute_import

from astrokat.jsontools import ObsJSON


class Catalogue(object):
    """Unpack catalogue, assuming comma-separated values.

    Parameters
    ----------
    filename: file with no header lines are allowed, only target information
          Input format: name, tags, ra, dec

    Returns
    --------
        List of json targets

    """

    def __init__(self, filename):
        self.infile = filename
        self.header = ""
        self.json = ObsJSON()

    def tidy_tags(self, tags):
        """Cleanup catalogue tags and construct expected tag format."""
        tags = tags.split()
        # add target tag if not a calibrator
        if not any("cal" in tag for tag in tags):
            if "target" not in tags:
                tags.append("target")
        return " ".join(tags)

    def target_list(self,
                    target_duration="",
                    gaincal_duration="",
                    bpcal_duration="",
                    bpcal_interval=None,
                    ):
        """Unpack all targets from catalogue files into list.

        Parameters
        ----------
        target_duration: float
            Duration on target
        gaincal_duration: float
            Duration on gain calibrator
        bpcal_duration: float
            Duration on bandpass calibrator
        bpcal_interval: flat
            How frequent to visit the bandpass calibrator

        """
        with open(self.infile, "r") as fin:
            for idx, line in enumerate(fin.readlines()):
                line = line.strip()

                # keep header information
                if line[0] == "#":
                    self.header += '{}\n'.format(line)
                    continue

                # skip blank lines
                if len(line) < 2:
                    continue

                # unpack data columns
                data_columns = [each.strip() for each in line.split(",")]
                [name, tags, x_coord, y_coord] = data_columns[:4]
                flux_model = ''
                if len(data_columns) > 4:
                    flux_model = " ".join(data_columns[4:])
                    # skip empty brackets it means nothing
                    if len(flux_model[1:-1]) < 1:
                        flux_model = ''

                tags = self.tidy_tags(tags.strip())
                if tags.startswith("azel"):
                    coord_type = "azel"
                elif tags.startswith("gal"):
                    coord_type = "gal"
                else:
                    coord_type = "radec"
                if len(name) < 1:
                    name = "target{}_{}".format(idx, coord_type)

                cadence = ''
                if "target" in tags:
                    duration = target_duration
                elif "gaincal" in tags:
                    duration = gaincal_duration
                else:
                    duration = bpcal_duration
                    if bpcal_interval is not None:
                        cadence = bpcal_interval

                self.json.add_target(name,
                                     x_coord,
                                     y_coord,
                                     duration,
                                     tags,
                                     coord_type=coord_type,
                                     flux_model=flux_model,
                                     cadence=cadence)

    def target2string(self, target_list):
        """Create yaml target list

        Parameters
        ----------
            target_list: list
                A list of json targets

        Returns
        --------
            targets: list
                A list of targets with the format
                'name=<name>, <coord_type>=<x_coord>,<y_coord>, tags=<tags>, duration=<sec>'

        """
        targets = []
        for target in target_list:
            target_items = [target['name'],
                            target['coord_type'],
                            " ".join([target['x'], target['y']]),
                            target['tags'],
                            target['duration']]
            target_spec = "name={}, {}={}, tags={}, duration={}"
            if target['cadence']:
                target_spec += ", cadence={}"
                target_items.append(target['cadence'])
            if target['flux_model']:
                target_spec += ", model={}"
                target_items.append(target['flux_model'])
            target = target_spec.format(*target_items)
            targets.append(target)
        return targets

# -fin-
