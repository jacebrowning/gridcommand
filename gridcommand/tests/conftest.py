"""Unit tests configuration file."""

from .fixtures import *  # pylint: disable=wildcard-import,unused-wildcard-import


def pytest_configure(config):
    """Disable verbose output when running tests."""
    terminal = config.pluginmanager.getplugin('terminal')
    base = terminal.TerminalReporter

    class QuietReporter(base):
        """A py.test reporter that only shows dots when running tests."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.verbosity = 0
            self.showlongtestinfo = False
            self.showfspath = False

    terminal.TerminalReporter = QuietReporter
