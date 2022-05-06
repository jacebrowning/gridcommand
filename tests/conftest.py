import log


def pytest_configure(config):
    log.silence("faker")
    terminal = config.pluginmanager.getplugin("terminal")
    terminal.TerminalReporter.showfspath = False
