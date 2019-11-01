""" JSON definition and packaging """

from __future__ import division
from __future__ import absolute_import

from collections import OrderedDict
import json

template = """
{
    "name": "",
    "id": 0,
    "description": null,
    "proposal_id": "",
    "state": "DRAFT",
    "owner": "",
    "sb_id": 0,
    "calendar_event_url": "",
    "instrument": {},
    "noise_diode": {},
    "horizon": 20,
    "lst_start": "0",
    "lst_start_end": null,
    "desired_start_time": null,
    "duration": "",
    "blocks": [
        {
            "name": "Block",
            "repeat": 1,
            "targets": []
        }
    ],
    "activities": [],
    "flux_bandpass_calibrators": [],
    "polarisation_calibrators": [],
    "isYamlObservation": "false"
}
"""

instrument_structure = """
{
    "enabled": false,
    "product": "",
    "integration_period": "",
    "band": "",
    "pool_resources": [
        "cbf",
        "sdp"
    ]
}
"""

noise_diode_setup = """
{
    "enabled": false,
    "pattern": "all",
    "on_fraction": null,
    "cycle_len": null
}
"""

# "ra": "",  # need to make this x (ra, lon, gal)
# "dec": "",  # need to make this y (dec, lat, gal)
empty_target = """
{
    "name": "",
    "coord_type": "",
    "x": "",
    "y": "",
    "tags": [],
    "type": "",
    "duration": 0,
    "cadence": 0,
    "flux_model": ""
}
"""


class ObsJSON(object):
    """Construct json object from template."""

    def __init__(self):
        self.observation = json.loads(template,
                                      object_pairs_hook=OrderedDict)
        self.instrument = {}
        self.targets = []

    def add_instrument(self,
                       instrument):
        self.instrument = json.loads(instrument_structure,
                                     object_pairs_hook=OrderedDict)
        for key, value in instrument.iteritems():
            # # !!this should not be dump_rate!!
            # if key == 'integration_period':
            #     key = 'dump_rate'
            self.instrument[key] = value

    def add_target(self,
                   name,
                   x_coord,
                   y_coord,
                   duration,
                   tags=[],
                   coord_type='radec',
                   obs_type='track',
                   cadence=0,
                   flux_model=''):
        """Construct json target object from definition."""

        if tags:
            tags = tags[len(tags.split()[0]):].strip()

        target = json.loads(empty_target,
                            object_pairs_hook=OrderedDict).copy()
        target["name"] = name
        target["coord_type"] = coord_type
        target["x"] = x_coord
        target["y"] = y_coord
        target["tags"] = tags
        target["type"] = obs_type
        target["duration"] = duration
        target["cadence"] = cadence
        target["flux_model"] = flux_model

        self.targets.append(target)


def write(filename, json_dict):
    """Write the json observation file."""
    with open(filename, 'w') as j_out:
        json.dump(json_dict, j_out)


def read(filename):
    """Read the json observation file."""
    with open(filename) as j_in:
        return json.load(j_in,
                         object_pairs_hook=OrderedDict)


def view(filename='',
         json_dict=None):
    """Prettry-print json observation"""
    if filename:
        json_dict = read(filename)
    print(json.dumps(json_dict,
                     ensure_ascii=False,
                     indent=4))

# -fin-
