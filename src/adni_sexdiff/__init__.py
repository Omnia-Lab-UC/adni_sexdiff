"""adni_sexdiff package

Sex × stage (CN / MCI / AD) trajectory comparison on ADNI serum metabolomics
(Biocrates p180 and Nightingale NMR) with MOTCO. Python >=3.12 with pandas
and numpy managed via uv.

ADNI is controlled-access: nothing participant-level leaves the machine it
was made on or enters version control (see ``AGENTS.md``).

Importing this package sets the pinned numeric environment
(``constants.NUMERIC_SETTINGS``: numpy's CPU dispatch, OpenBLAS's kernel and
thread count, OpenMP's thread count) in ``os.environ``, replacing any other
value, before any of its modules imports numpy. The settings change how
floating-point operations are dispatched, not what is computed, and make
every machine write the same bytes from the same inputs. They apply to this
process and its children only, and only when numpy and OpenBLAS have not yet
been loaded: import ``adni_sexdiff`` before numpy. Every step's manifest
records the state the process actually had (``numerics``) and a finding when
it is not pinned.
"""

import os as _os

from .constants import NUMERIC_SETTINGS as _NUMERIC_SETTINGS

_os.environ.update(_NUMERIC_SETTINGS)

__all__ = ["__version__"]

__version__ = "0.1.0"
