SydGigs
=======

Nobody but me will read this, but I will still format & document it beautifully.

A website that tracks:

* Gigs,
* The artists who play them,
* The venues who host them,

Runs as a Python app and is currently NOT PRODUCTION READY.

Requirements
------------

* Python 2.6/2.7
* virtualenv (if not already installed, try `sudo pip install virtualenv` or `sudo easy_install virtualenv`

Installation
------------

This repository is intended to be used with a Python virtualenv. This is a Python install in a single directory, which means no need to pollute your system with the real requirements. You just need virtualenv installed system wide. If you can't run 'virtualenv', you need to install it:

1. `cd sydgig`
2. `virtualenv venv`
3. `. ./venv/bin/activate` (Unix) or `venv\Scripts\Activate` (Windows)
4. `pip install -r requirements.txt`

How to run the site
-------------------

There are two daemons:

* The website - `./runwebsite.sh`
* The task queue - `./runtaskqueue.sh`

You need to run both from the base directory of sydgig.
