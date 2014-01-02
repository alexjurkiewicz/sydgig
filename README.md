SydGigs
=======

Nobody but me will read this, but I will still format & document it beautifully.

A website that tracks:

* Gigs,
* The artists who play them,
* The venues who host them,

Runs as a Python app and is currently SORTA PRODUCTION READY.

Requirements
------------

* Python 2.6/2.7
* virtualenv (if not installed, try `sudo pip install virtualenv` or `sudo easy_install virtualenv`)

Installation
------------

This repository is intended to be used with a Python virtualenv. This is a Python install in a single directory, which means no need to pollute your system with the real requirements. You just need virtualenv installed system wide. If you can't run `virtualenv`, you need to install it:

1. `cd sydgig`
2. `virtualenv venv`
3. `. ./venv/bin/activate` (Unix) or `venv\Scripts\Activate` (Windows)
4. `pip install -r requirements.txt`

(If you ever want to upgrade these dependencies later, use `pip install -U -r requirements.txt`.)

How to run the site
-------------------

Firstly, create config.ini and edit it:

1. `cp config.ini.sample config.ini`
2. `vi config.ini`

SydGig as a running application has two components: the website and the background task queue. In dev, you can start these components with `./runwebsite.sh` and `./runtaskqueue.sh`. In prod, you should host the website using a real server. Here's how to do it with Ubuntu + nginx + uwsgi.

1. Install `uwsgi`, `uwsgi-plugin-python`, `uwsgi-extra` and `nginx`. Add config like this to nginx.conf:

        server {
            listen          [::]:80;
            server_name sydgig.com www.sydgig.com;
            location {
                include /usr/share/doc/uwsgi-extra/nginx/uwsgi_params;
                uwsgi_param SCRIPT_NAME /;
                uwsgi_modifier1 30;
                uwsgi_pass unix:/tmp/sydgig.sock;
            }
        }

2. Run the uwsgi backend:

        uwsgi_python -s /tmp/sydgig.sock --module sydgig --callable app -H venv

3. Change the socket permissions so nginx can access it: `chgrp www-data /tmp/sydgig.sock`. (Better: Use uwsgi\_python's `--uid` and `--gid` to run the app as a zero-permissions user and add www-data to that group.)

3. Start the task queue in the same manner as dev: `./runtaskqueue.sh`

Hacking
-------

The filesystem layout is currently poor, and logical layers it suggests exist aren't very cleanly separated in code. Fixing these things will happen Eventually.

Overview of each file:

* `sydgig/__init__.py`: HTTPd logic (URL routing, template selection, form parsing, etc) (Flask)
* `sydgig/template/`: Website static content templates (Jinja)
* `sydgig/template.py`: Jinja support (template loader, custom templates)
* `sydgig/database.py`: DB connection & ORM (SQLAlchemy)
* `sydgig/model.py`: SydGig business logic
* `sydgig/util.py`: Miscellaneous support functions
* `sydgig/tasks.py`: Task queue jobs (Celery)
* `sydgig/config.py`: SydGig application-level config
* `sydgig/googlemaps_api.py`, `sydgig/lastfm_api.py`, `sydgig/lib/`: Supporting libraries
* `sydgig/static/`: Runtime application data (js, css, artist images)

These layers aren't currently cleanly separated - specifically, ORM objects go everywhere, whereas their access should really be mediated through `model.py`.
