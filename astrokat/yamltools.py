""" YAML definition and packaging """

from __future__ import division
from __future__ import absolute_import

from contextlib import contextmanager

import sys


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

# -fin-
