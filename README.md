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

SydGig has two components: the website and the task queue/runner.

In dev, you can start the components using `./runwebsite.sh` and `./runtaskqueue.sh`.

In prod, you should host the application using a better web server than Flask's built-in one. Here's how to do it with Ubuntu + nginx + uwsgi.

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

   (You'll probably also need to change the socket permissions so nginx can access it: `chgrp www-data /tmp/sydgig.sock`. Or if you prefer, run uwsgi\_python with `--uid www-data --gid www-data`.)

3. Start the task queue in the same manner as dev: `./runtaskqueue.sh`
