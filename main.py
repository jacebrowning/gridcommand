#!/usr/bin/env python3

"""Entry point for GridCommand."""

from gridcommand import app
from gridcommand import data


if __name__ == "__main__":
    data.load()
    app.run(debug=True)
