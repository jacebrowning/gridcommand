#!/usr/bin/env python3

from gridcommand.views import app
from gridcommand import models


if __name__ == "__main__":
    models.load()
    app.run(debug=True)
