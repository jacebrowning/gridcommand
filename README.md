GridCommand
======
TBD

[![Build Status](http://img.shields.io/travis/jacebrowning/gridcommand/master.svg)](https://travis-ci.org/jacebrowning/gridcommand)
[![Coverage Status](http://img.shields.io/coveralls/jacebrowning/gridcommand/master.svg)](https://coveralls.io/r/jacebrowning/gridcommand)
[![Scrutinizer Code Quality](http://img.shields.io/scrutinizer/g/jacebrowning/gridcommand.svg)](https://scrutinizer-ci.com/g/jacebrowning/gridcommand/?branch=master)
[![PyPI Version](http://img.shields.io/pypi/v/GridCommand.svg)](https://pypi.python.org/pypi/GridCommand)
[![PyPI Downloads](http://img.shields.io/pypi/dm/GridCommand.svg)](https://pypi.python.org/pypi/GridCommand)


Getting Started
===============

Requirements
------------

* Python 3.4+

Installation
------------

GridCommand can be installed with pip:

```
$ pip install GridCommand
```

or directly from the source code:

```
$ git clone https://github.com/jacebrowning/gridcommand.git
$ cd gridcommand
$ python setup.py install
```

Basic Usage
===========

After installation, abstract base classes can be imported from the package:

```
$ python
>>> import gridcommand
gridcommand.__version__
```

GridCommand doesn't do anything, it's a template.

For Contributors
================

Requirements
------------

* Make:
    * Windows: http://cygwin.com/install.html
    * Mac: https://developer.apple.com/xcode
    * Linux: http://www.gnu.org/software/make (likely already installed)
* virtualenv: https://pypi.python.org/pypi/virtualenv#installation
* Pandoc: http://johnmacfarlane.net/pandoc/installing.html
* Graphviz: http://www.graphviz.org/Download.php

Installation
------------

Create a virtualenv:

```
$ make env
```

Run the tests:

```
$ make test
$ make tests  # includes integration tests
```

Build the documentation:

```
$ make doc
```

Run static analysis:

```
$ make pep8
$ make pep257
$ make pylint
$ make check  # includes all checks
```

Prepare a release:

```
$ make dist  # dry run
$ make upload
```
