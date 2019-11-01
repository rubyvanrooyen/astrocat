#!/usr/bin/env python
"""Take a catalogue file and construct a observation configuration file."""

from __future__ import print_function

from astrokat import (Observatory,
                      catalogue,
                      jsontools,
                      yamltools,
                      __version__)
import argparse
import argcomplete


def cli():
    """Parse command line options.

    Returns
    -------
    option arguments

    """
    usage = "%(prog)s [options] --csv <full_path/cat_file.csv>"
    description = ("sources are specified as a catalogue of targets, "
                   "with optional timing information")

    parser = argparse.ArgumentParser(
        usage=usage,
        description=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--version",
                        action="version",
                        version=__version__)
    parser.add_argument("--csv",
                        type=str,
                        required=True,
                        help="filename of the input CSV catalogue "
                             "(**required**)")
    parser.add_argument("--yaml",
                        type=str,
                        help="filename for observation YAML file "
                             "(default outputs to screen)")
    parser.add_argument("--json",
                        type=str,
                        help="filename for observation JSON file")
    parser.add_argument("--show",
                        action="store_true",
                        help="Show observation JSON instructions")

    description = "instrument setup requirements"
    group = parser.add_argument_group(title="observation instrument setup",
                                      description=description)
    group.add_argument("--product",
                       type=str,
                       help="observation instrument product configuration")
    group.add_argument("--band",
                       type=str,
                       help="observation band: L, UHF, X, S")
    group.add_argument("--integration-period",
                       type=float,
                       help="averaging time per dump [sec]")

    description = ("track a target for imaging or spectral line observations, "
                   "may optionally have a tag of 'target'.")
    group = parser.add_argument_group(title="target observation strategy",
                                      description=description)
    group.add_argument("--lst",
                       type=str,
                       help="observation start LST")
    group.add_argument("--target-duration",
                       type=float,
                       default=300,  # sec
                       help="default target track duration [sec]")
    group.add_argument("--horizon",
                       type=float,
                       help="Minimum horizon angle [deg]")
    group.add_argument("--max-duration",
                       type=float,
                       help="maximum duration of observation [sec]")

    description = ("calibrators are identified by tags "
                   "in their description strings: "
                   "'bpcal', 'gaincal', 'fluxcal' and 'polcal' respectively")
    group = parser.add_argument_group(title="calibrator observation strategy",
                                      description=description)
    group.add_argument("--primary-cal-duration",
                       type=float,
                       default=300,  # sec
                       help="duration to track primary calibrators tagged as "
                       "'bpcal', 'fluxcal' or 'polcal' [sec]")
    group.add_argument("--primary-cal-cadence",
                       type=float,
                       help="interval between calibrator observation [sec]")
    group.add_argument("--secondary-cal-duration",
                       type=float,
                       default=60,  # sec
                       help="duration to track gain calibrator [sec]")
    argcomplete.autocomplete(parser)
    return parser


class BuildObservation(object):
    """Create default observation config

    Parameters
    ----------
    target_list: list
        A list of targets with the format
        'name=<name>, radec=<HH:MM:SS.f>,<DD:MM:SS.f>, tags=<tags>, duration=<sec>'

    """

    def __init__(self,
                 cat_obj,
                 instrument={}):
        self.configuration = cat_obj.json.observation
        self.targets = cat_obj.json.targets
        self.target_list = catalogue.target2string(self.targets)
        self.instrument = instrument
        if instrument:
            cat_obj.json.add_instrument(instrument)
            self.instrument = cat_obj.json.instrument

    def configure(self,
                  horizon=None,
                  obs_duration=None,
                  lst=None):
        """Set up of the MeerKAT telescope for running observation.

        Parameters
        ----------
        horizon: float
            Minimum observation angle
        obs_duration: float
            Duration of observation
        lst: datetime
            Local Sidereal Time at telescope location

        """
        # subarray specific setup options
        self.configuration["instrument"] = self.instrument

        # set observation duration if specified
        self.configuration['duration'] = int(obs_duration or 0)

        if horizon is not None:
            self.configuration['horizon'] = horizon

        # LST times only HH:MM in OPT
        if lst is None:
            start_lst = Observatory().start_obs(self.target_list,
                                                str_flag=True)
            self.configuration["lst_start"] = ":".join(start_lst.split(":")[:-1])
        # observational setup
        self.configuration['blocks'][0]['targets'] = self.targets


if __name__ == "__main__":
    parser = cli()
    args = parser.parse_args()

    # read instrument requirements if provided
    instrument = {}
    for group in parser._action_groups:
        if "instrument setup" in group.title:
            group_dict = {
                a.dest: getattr(args, a.dest, None) for a in group._group_actions
            }
            instrument = vars(argparse.Namespace(**group_dict))
            break
    for key in instrument.keys():
        if instrument[key] is None:
            del instrument[key]

    # read targets from catalogue file
    cat_obj = catalogue.Catalogue(args.csv)
    cat_obj.target_list(target_duration=args.target_duration,
                        gaincal_duration=args.secondary_cal_duration,
                        bpcal_duration=args.primary_cal_duration,
                        bpcal_interval=args.primary_cal_cadence)
    obs_plan = BuildObservation(cat_obj,
                                instrument=instrument)

    # create observation configuration JSON
    obs_plan.configure(horizon=args.horizon,
                       obs_duration=args.max_duration,
                       lst=args.lst)

    # write observation configuration to file
    if args.json:
        jsontools.write(args.json,
                        obs_plan.configuration)
        if args.show:
            jsontools.view(filename=args.json)
    elif args.show:
        jsontools.view(json_dict=obs_plan.configuration)

    # unpack to create yaml structure
    yaml_obj = yamltools.ObsYAML(instrument=obs_plan.instrument,
                                 horizon=obs_plan.configuration['horizon'],
                                 durations={'obs_duration':
                                            obs_plan.configuration['duration']})
    yaml_obj.write(args.yaml,
                   obs_plan.configuration['lst_start'],
                   obs_plan.target_list,
                   header=cat_obj.header)

# -fin-
