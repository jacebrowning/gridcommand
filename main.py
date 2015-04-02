#!/usr/bin/env python3

from gridcommand import app
from gridcommand import data


if __name__ == "__main__":
    data.load()
    app.run(debug=True)
