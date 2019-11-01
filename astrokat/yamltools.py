""" YAML definition and packaging """

from __future__ import division
from __future__ import absolute_import

from astrokat.jsontools import ObsJSON
from contextlib import contextmanager

from astrokat import jsontools

import datetime
import numpy
import sys
import yaml


@contextmanager
def smart_open(filename):
    """Open catalogue file."""
    if filename and filename != "-":
        with open(filename, "w") as fout:
            yield fout
    else:
        yield sys.stdout


class ObsYAML(object):
    """Construct yaml structure from JSON objects"""
    def __init__(self,
                 instrument={},
                 horizon='',
                 noise_diode={},
                 scans={},
                 durations={},
                 ):
        self.setup = ""
        # instrument definition
        if instrument:
            self.setup += self.yaml_block('instrument',
                                          instructions=instrument)
        # observation limit
        if horizon:
            self.setup += self.yaml_block('horizon',
                                          value=horizon)
        # noise diode setup
        # 'noise_diode'
        # scan types

        # observation durations
        if durations:
            # 'desired_start_time', 'duration',
            if durations['obs_duration'] > 0:
                self.setup += self.yaml_block('durations',
                                              instructions=durations)

    def yaml_block(self,
                   name,
                   value='',
                   instructions={}):
        if value:
            block_str = "{}: {}\n".format(name, value)
        else:
            block_str = "{}:\n".format(name)
        for key, value in instructions.iteritems():
            if isinstance(value, list):
                value = ','.join(value)
            block_str += "  {}: {}\n".format(key, value)
        return block_str

    def write(self,
              filename,
              lst,
              targets,
              header=""):
        """Write the yaml observation file."""

        instruction_set = ""
        instruction_set += header
        instruction_set += self.setup
        instruction_set += "{}:\n".format("observation_loop")
        instruction_set += "  - LST: {}\n".format(lst)
        instruction_set += "    {}:\n".format("target_list")
        for target in targets:
            instruction_set += "      - {}\n".format(target)

        with smart_open(filename) as fout:
            fout.write(instruction_set)


def write2json(dict_):
    json_obj = ObsJSON()
    if 'instrument' in dict_:
        instrument = dict_['instrument']
        if 'dump_rate' in instrument:
            dump_rate = float(instrument["dump_rate"])
            instrument["integration_time"] = 1.0 / dump_rate
            del instrument["dump_rate"]
        json_obj.add_instrument(instrument)
        json_obj.observation['instrument'] = json_obj.instrument

    if 'horizon' in dict_:
        json_obj.observation['horizon'] = dict_['horizon']

    if 'durations' in dict_:
        durations = dict_['durations']
        if 'start_time' in durations:
            date_time = durations['start_time']
            d = date_time.strftime("%Y-%m-%d %H:%M:%SZ")
            json_obj.observation['desired_start_time'] = d
        if 'obs_duration' in durations:
            json_obj.observation['duration'] = durations['obs_duration']

    if 'noise_diode' in dict_:
        noise_diode = dict_['noise_diode']
        json_obj.add_nd(noise_diode)
        json_obj.observation['noise_diode'] = json_obj.noise_diode

    if 'scan' in dict_:
        scan = dict_['scan']
        scan['start'] = scan['start'].tolist()
        scan['end'] = scan['end'].tolist()
        json_obj.add_scan(scan)
        json_obj.observation['scan'] = json_obj.scan

    if 'raster_scan' in dict_:
        raster_scan = dict_['raster_scan']
        json_obj.add_raster_scan(raster_scan)
        json_obj.observation['raster_scan'] = json_obj.raster_scan

    lst = str(dict_['observation_loop'][0]['LST'])
    json_obj.observation['lst_start'] = lst.split('-')[0]

    # target_list = dict_['observation_loop'][0]['target_list']
    # need to find a better implementation from observe_main
    jsontools.view(json_dict=json_obj.observation)


def read(filename):
    """Read config .yaml file."""
    with open(filename, "r") as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.parser.ParserError:
            return {}

    if not isinstance(data, dict):
        # not a yaml file, suspected csv file, returning False
        return {}

    # remove empty keys
    for key in list(data.keys()):
        if data[key] is None:
            del data[key]

    # handle mapping of user friendly keys to CAM resource keys
    if "instrument" in data.keys():
        instrument = data["instrument"]
        if instrument is not None:
            if "integration_time" in instrument.keys():
                integration_time = float(instrument["integration_time"])
                instrument["dump_rate"] = 1.0 / integration_time
                del instrument["integration_time"]

    # verify required information in observation loop before continuing
    if "durations" in data.keys():
        if data["durations"] is None:
            msg = "Durations primary key cannot be empty in YAML file"
            raise RuntimeError(msg)
        if "start_time" in data["durations"]:
            start_time = data["durations"]["start_time"]
            if isinstance(start_time, str):
                data["durations"]["start_time"] = datetime.datetime.strptime(
                    start_time, "%Y-%m-%d %H:%M"
                )
    if "observation_loop" not in data.keys():
        raise RuntimeError("Nothing to observe, exiting")
    if data["observation_loop"] is None:
        raise RuntimeError("Empty observation loop, exiting")
    for obs_loop in data["observation_loop"]:
        if isinstance(obs_loop, str):
            raise RuntimeError(
                "Incomplete observation input: "
                "LST range and at least one target required."
            )
        # TODO: correct implementation for single vs multiple observation loops
        # -> if len(obs_loop) > 0:
        if "LST" not in obs_loop.keys():
            raise RuntimeError("Observation LST not provided, exiting")
        if "target_list" not in obs_loop.keys():
            raise RuntimeError("Empty target list, exiting")

    if "scan" in data.keys():
        if "start" in data["scan"].keys():
            scan_start = data["scan"]["start"].split(",")
            data["scan"]["start"] = numpy.array(scan_start, dtype=float)
        if "end" in data["scan"].keys():
            scan_end = data["scan"]["end"].split(",")
            data["scan"]["end"] = numpy.array(scan_end, dtype=float)

    return data


# -fin-
