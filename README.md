# GridCommand

[![Build Status](http://img.shields.io/travis/jacebrowning/gridcommand/master.svg)](https://travis-ci.org/jacebrowning/gridcommand)
[![Coverage Status](http://img.shields.io/coveralls/jacebrowning/gridcommand/master.svg)](https://coveralls.io/r/jacebrowning/gridcommand)
[![Scrutinizer Code Quality](http://img.shields.io/scrutinizer/g/jacebrowning/gridcommand.svg)](https://scrutinizer-ci.com/g/jacebrowning/gridcommand/?branch=master)

## Prerequisites

You will need the following things installed on your computer:

* [Python](https://www.python.org/): `$ brew install pyenv && pyenv install 3.5.0`

To confirm these system dependencies are configured correctly:

```
$ make doctor
```

## Installation

Clone this repository:

```
$ git clone <repository url>
$ cd <new directory>
```

Install the project dependencies:

```
$ make install
```

## Configuration

N/A

## Basic Usage

Run all tests and checks:

```
$ make ci
```

Run the server:

```
$ make run
```
