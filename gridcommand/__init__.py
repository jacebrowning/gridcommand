"""Package for GridCommand."""

import sys

__project__ = 'GridCommand'
__version__ = '0.1.dev0'

VERSION = __project__ + '-' + __version__

PYTHON_VERSION = 3, 3

if not sys.version_info >= PYTHON_VERSION:  # pragma: no cover
    exit("Python {}.{}+ is required.".format(*PYTHON_VERSION))
