#!env/bin/python

import os

from flask_script import Manager, Server

# TODO: add app.py and settings.py to match other Flask applications
# from gridcommand.settings import get_config
# from gridcommand.app import create_app
from gridcommand.routes import app


def find_assets():
    """Yield paths for all static files and templates."""
    for name in ['static', 'templates']:
        directory = os.path.join(app.config['PATH'], name)
        for entry in os.scandir(directory):
            if entry.is_file():
                yield entry.path


# TODO: add app.py and settings.py to match other Flask applications
# config = get_config(os.getenv('FLASK_ENV'))

# app = create_app(config)

server = Server(host='0.0.0.0', extra_files=find_assets())

manager = Manager(app)
manager.add_command('run', server)


if __name__ == '__main__':
    manager.run()
