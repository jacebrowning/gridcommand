GridCommand
===========

[![Build Status](http://img.shields.io/travis/jacebrowning/gridcommand/master.svg)](https://travis-ci.org/jacebrowning/gridcommand)
[![Coverage Status](http://img.shields.io/coveralls/jacebrowning/gridcommand/master.svg)](https://coveralls.io/r/jacebrowning/gridcommand)
[![PyPI Version](http://img.shields.io/pypi/v/gridcommand.svg)](https://pypi.python.org/pypi/gridcommand)
[![PyPI Downloads](http://img.shields.io/pypi/dm/gridcommand.svg)](https://pypi.python.org/pypi/gridcommand)

GridCommand is TBA.



Getting Started
===============

Requirements
------------

* Python 3.3+


Installation
------------

GridCommand can be installed with 'pip':

    pip install GridCommand

Or directly from the source code:

    git clone https://github.com/jacebrowning/gridcommand.git
    cd gridcommand
    python setup.py install



Basic Usage
===========

GridCommand doesn't do anything yet.



For Contributors
================

Requirements
------------

* GNU Make:
    * Windows: http://cygwin.com/install.html
    * Mac: https://developer.apple.com/xcode
    * Linux: http://www.gnu.org/software/make (likely already installed)
* virtualenv: https://pypi.python.org/pypi/virtualenv#installation
* Pandoc: http://johnmacfarlane.net/pandoc/installing.html
* Graphviz: http://www.graphviz.org/Download.php


Installation
------------

Create a virtualenv:

    make env

Run the tests:

    make test
    make tests  # includes integration tests

Build the documentation:

    make doc

Run static analysis:

    make pep8
    make pep257
    make pylint
    make check  # includes all checks

Prepare a release:

    make dist  # dry run
    make upload
