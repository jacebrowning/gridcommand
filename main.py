#!/usr/bin/env python3

"""Entry point for GridCommand."""

from gridcommand import app, data


if __name__ == "__main__":
    data.load()
    app.run(debug=True)
