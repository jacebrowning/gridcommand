#!/usr/bin/env python3

"""Entry point for GridCommand."""

import sys

from gridcommand import app


def main():
    debug = ('--debug' in sys.argv)
    public = ('--public' in sys.argv)

    run(debug, public)


def run(debug, public):
    kwargs = dict(debug=debug)
    if public:
        kwargs.update(host='0.0.0.0')

    app.run(**kwargs)


if __name__ == "__main__":
    main()
