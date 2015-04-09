#!/usr/bin/env python3

"""Entry point for GridCommand."""

import sys

from gridcommand import app, data


def main():
    debug = ('--debug' in sys.argv)
    public = ('--public' in sys.argv)

    run(debug, public)


def run(debug, public):
    kwargs = {'debug': debug}
    if public:
        kwargs['host'] = '0.0.0.0'

    data.load()

    app.run(**kwargs)


if __name__ == "__main__":
    main()
