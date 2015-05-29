import os
import time
import subprocess

from sniffer.api import select_runnable, file_validator, runnable
try:
    from pync import Notifier
except ImportError:
    notify = None
else:
    notify = Notifier.notify


watch_paths = ['gridcommand/', 'tests/']


@select_runnable('python_tests')
@file_validator
def py_files(filename):
    return all((filename.endswith('.py'),
               not os.path.basename(filename).startswith('.')))


@runnable
def python_tests(*_):

    group = int(time.time())  # unique per run

    for count, (command, title) in enumerate((
        (('make', 'test-unit'), "Unit Tests"),
        (('make', 'test-int'), "Integration Tests"),
        (('make', 'test-all'), "Combined Tests"),
    ), start=1):

        failure = subprocess.call(command)

        if failure:
            if notify:
                mark = "❌" * count
                notify(mark + " [FAIL] " + mark, title=title, group=group)
            return False
        else:
            if notify:
                mark = "✅" * count
                notify(mark + " [PASS] " + mark, title=title, group=group)

    return True
