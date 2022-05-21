import datafiles
import log


def pytest_configure(config):
    log.silence("faker")
    log.silence("datafiles", allow_info=True)
    terminal = config.pluginmanager.getplugin("terminal")
    terminal.TerminalReporter.showfspath = False


def pytest_runtest_setup(item):
    datafiles.settings.HOOKS_ENABLED = False
