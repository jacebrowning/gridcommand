"""Package for GridCommand."""

import sys

__project__ = 'GridCommand'
__version__ = '0.1dev0'

VERSION = __project__ + '-' + __version__

PYTHON_VERSION = 3, 3

if not sys.version_info >= PYTHON_VERSION:  # pragma: no cover (manual test)
    exit("Python {}.{}+ is required.".format(*PYTHON_VERSION))

try:
    from .routes import app
except (ImportError, AttributeError):  # pragma: no cover (manual test)
    import logging
    logging.exception("dependencies:")
