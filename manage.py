#!env/bin/python

import os

from flask_script import Manager, Server

from gridcommand.config import load
from gridcommand.app import build


def find_assets():
    """Yield paths for all static files and templates."""
    for name in ['static', 'templates']:
        directory = os.path.join(app.config['PATH'], name)
        for entry in os.scandir(directory):
            if entry.is_file():
                yield entry.path


config = load(os.getenv('FLASK_ENV'))

app = build(config)

server = Server(host='0.0.0.0', extra_files=find_assets())

manager = Manager(app)
manager.add_command('run', server)


if __name__ == '__main__':
    manager.run()
