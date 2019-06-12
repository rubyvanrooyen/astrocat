from __future__ import division
from __future__ import absolute_import

from .__main__ import cli  # noqa

from .noisediode  import * # noqa
from .correlator  import * # noqa
from .scans import * # noqa

from .simulate import (  # noqa
    user_logger,
    verify_and_connect,
    start_session,
    )
from .utility import (  # noqa
    NoTargetsUpError,
    NotAllTargetsUpError,
    read_yaml,
    katpoint_target,
    get_lst,
    lst2utc,
    datetime2timestamp,
    timestamp2datetime,
    )
from .observatory import (  # noqa
    Observatory,
    collect_targets,
    )


# BEGIN VERSION CHECK
# Get package version when locally imported from repo or via -e develop install
try:
    import katversion as _katversion
except ImportError:
    import time as _time
    __version__ = "0.0+unknown.{}".format(_time.strftime('%Y%m%d%H%M'))
else:
    __version__ = _katversion.get_version(__path__[0])
# END VERSION CHECK

# -fin-
