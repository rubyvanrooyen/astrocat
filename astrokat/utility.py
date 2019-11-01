"""Astrokat utilities."""
import datetime
import katpoint
import numpy
import time


class NotAllTargetsUpError(Exception):
    """Raise error when not all targets are at the desired horizon.

    Not all targets are above the horizon at the start of the observation error

    """


class NoTargetsUpError(Exception):
    """No targets are above the horizon at the start of the observation."""


def datetime2timestamp(datetime_obj):
    """Safely convert a datetime object to a UTC timestamp.

    UTC seconds since epoch, reverse of `timestamp2datetime`
    method described in this module

    """
    epoch = datetime.datetime.utcfromtimestamp(0)
    return (datetime_obj - epoch).total_seconds()


def timestamp2datetime(timestamp):
    """Safely convert a timestamp to UTC datetime object.

    UTC datetime object, reverse of `datetime2timestamp`
    method described in this module

    """
    return datetime.datetime.utcfromtimestamp(timestamp)


def katpoint_target(target_item):
    """Construct an expected katpoint target from a target_item string."""
    coords = ["radec", "azel", "gal"]
    # input string format: name=, radec=, tags=, duration=, ...
    target_ = [item.strip() for item in target_item.split(",")]
    for item_ in target_:
        prefix = "name="
        if item_.startswith(prefix):
            name = item_[len(prefix):]
        prefix = "tags="
        if item_.startswith(prefix):
            tags = item_[len(prefix):]
        prefix = "model="
        if item_.startswith(prefix):
            fluxmodel = item_[len(prefix):]
        else:
            fluxmodel = ()
        for coord in coords:
            prefix = coord + "="
            if item_.startswith(prefix):
                ctag = coord
                x = item_[len(prefix):].split()[0].strip()
                y = item_[len(prefix):].split()[1].strip()
                break
    target = "{}, {} {}, {}, {}, {}".format(name, ctag, tags, x, y, fluxmodel)
    return name, target


def get_lst(yaml_lst):
    """Extract lst range from YAML key.

    Get the Local Sidereal Time range for when a celestial body can be observed
    from the YAML file of targets in config

    """
    start_lst = None
    end_lst = None
    # YAML input without quotes will calc this integer
    if isinstance(yaml_lst, int):
        HH = int(yaml_lst / 60)
        MM = yaml_lst - (HH * 60)
        yaml_lst = "{}:{}".format(HH, MM)
    # floating point hour format
    if isinstance(yaml_lst, float):
        HH = int(yaml_lst)
        MM = int(60 * (yaml_lst - HH))
        yaml_lst = "{}:{}".format(HH, MM)

    err_msg = "Format error reading LST range in observation file."
    if not isinstance(yaml_lst, str):
        raise RuntimeError(err_msg)

    nvals = len(yaml_lst.split("-"))
    if nvals < 2:
        start_lst = yaml_lst
    elif nvals > 2:
        raise RuntimeError(err_msg)
    else:
        start_lst, end_lst = [lst_val.strip() for lst_val in yaml_lst.split("-")]
    if ":" in start_lst:
        time_ = datetime.datetime.strptime("{}".format(start_lst), "%H:%M").time()
        start_lst = time_.hour + time_.minute / 60.0

    if end_lst is None:
        end_lst = (start_lst + 24.0) % 24.0
        if numpy.abs(end_lst - start_lst) < 1.0:
            end_lst = 24.0
    elif ":" in end_lst:
        time_ = datetime.datetime.strptime("{}".format(end_lst), "%H:%M").time()
        end_lst = time_.hour + time_.minute / 60.0
    else:
        end_lst = float(end_lst)

    return start_lst, end_lst


def lst2utc(req_lst, ref_location, date=None):
    """Find LST for given date else for Today.

    Parameters
    ----------
    req_lst: datetime
        Request LST
    ref_location: `EarthLocation()`
        Location on earth where LST is being measured
    date: datetime
        Date when LST is being measured

    Returns
    -------
        time_range: katpoint.Timestamp
            UTC date and time
        lst_range: float
            LST range

    """

    def get_lst_range(date):
        date_timestamp = time.mktime(date.timetuple())  # this will be local time
        time_range = katpoint.Timestamp(date_timestamp).secs + numpy.arange(
            0, 24.0 * 3600.0, 60
        )
        lst_range = numpy.degrees(target.antenna.local_sidereal_time(time_range)) / 15.0
        return time_range, lst_range

    req_lst = float(req_lst)
    cat = katpoint.Catalogue(add_specials=True)
    cat.antenna = katpoint.Antenna(ref_location)
    target = cat["Zenith"]
    if date is None:  # find the best UTC for today
        date = datetime.date.today()
    else:
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    [time_range, lst_range] = get_lst_range(date)
    lst_idx = numpy.abs(lst_range - req_lst).argmin()
    if lst_range[lst_idx] < req_lst:
        x = lst_range[lst_idx:lst_idx + 2]
        y = time_range[lst_idx:lst_idx + 2]
    else:
        x = lst_range[lst_idx - 1:lst_idx + 1]
        y = time_range[lst_idx - 1:lst_idx + 1]
    linefit = numpy.poly1d(numpy.polyfit(x, y, 1))
    return datetime.datetime.utcfromtimestamp(linefit(req_lst))


# -fin-
