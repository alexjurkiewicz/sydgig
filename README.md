Syd Gigs
========

Nobody but me will read this, but I will still format & document it beautifully.

A website that tracks:

* Gigs,
* The artists who play them,
* The venues who host them,
* The people who attend them.

Runs as a Python app and is currently NOT PRODUCTION READY.

Installation
------------

This repository is intended to be used with a Python virtualenv. This is a Python install in a single directory, which means no need to pollute your system with the real requirements. You just need virtualenv installed system wide. If you can't run 'virtualenv', you need to install it:

1. `sudo pip install virtualenv` or `sudo easy_install pip virtualenv` (no difference)
2. `cd /path/to/sydgig`
3. `virtualenv venv`. This creates a virtualenv in `venv/`.
4. `. ./venv/bin/activate` (Unix) or `venv\Scripts\Activate` (Windows). This will change your prompt to indicate the virtualenv is active.
5. `pip install -r requirements.txt`. This installs the requirements for the site into your virtualenv.
6. Done!

How to run the site
-------------------

There are two daemons:

* The website - `./runwebsite.sh`
* The task queue - `./runtaskqueue.sh`

You need to run both from the base directory of sydgig.
