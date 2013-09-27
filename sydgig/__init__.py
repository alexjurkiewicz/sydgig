from __future__ import division, absolute_import

import datetime, random, time

import sydgig.template as template
import sydgig.model as model

from flask import Flask, request, redirect, url_for, abort, g
app = Flask(__name__)
templates = template.templates

# Page timer
@app.before_request
def before_request():
  g.time_start = time.time()
@app.after_request
def after_request(response):
    diff = int((time.time() - g.time_start) * 1000)  # to get a time in ms
    if response.response and response.content_type.startswith("text/html") and response.status_code == 200:
        response.response[0] = response.response[0].replace('__EXECUTION_TIME__', str(diff))
        response.headers["content-length"] = len(response.response[0])
    return response

@app.route("/")
def index():
    template = templates.get_template("index.html")
    return template.render(gigs=model.get_gig_calendar())

@app.errorhandler(404)
def page_not_found(e):
    template = templates.get_template("404.html")
    response = template.render()
    # after_request handlers aren't run with the error handler, so calculate generation time here
    diff = int((time.time() - g.time_start) * 1000)  # to get a time in ms
    response = response.replace('__EXECUTION_TIME__', str(diff))
    return response, 404

@app.errorhandler(500)
def page_not_found(e):
    template = templates.get_template("500.html")
    response = template.render()
    # after_request handlers aren't run with the error handler, so calculate generation time here
    diff = int((time.time() - g.time_start) * 1000)  # to get a time in ms
    response = response.replace('__EXECUTION_TIME__', str(diff))
    return response, 500

@app.route('/about')
def about():
    vids = ( 'http://www.youtube.com/watch?v=M8XmoroZ3zo', # preatures - is this how you feel
            'http://www.youtube.com/watch?v=yBL3aKLZ6qY', # coach bombay - take off
            'http://www.youtube.com/watch?v=ED6yVA_zw7A', # client liaison @ golden plains
            'http://www.youtube.com/watch&v=ic1DjIFDbeQ', # the presets - fall
            )
    template = templates.get_template("about.html")
    return template.render(video=random.choice(vids))

# Artists
@app.route('/artist/<int:id>/<name>')
@app.route('/artist/<int:id>/')
def artist_info(id, name=None):
    template = templates.get_template("artist_info.html")
    return template.render(artist=model.get_artist_by_id(id))

# Venues
@app.route('/venue/<int:id>/<name>')
@app.route('/venue/<int:id>/')
def venue_info(id, name=None):
    template = templates.get_template("venue_info.html")
    return template.render(venue=model.get_venue_by_id(id))

# Gigs
@app.route('/gig/<int:id>')
def gig_info(id, name=None):
    template = templates.get_template("gig_info.html")
    return template.render(gig=model.get_gig_by_id(id))
