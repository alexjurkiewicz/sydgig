from __future__ import division, absolute_import

import datetime, random, time

import sydgig.template as template
import sydgig.model as model

from flask import Flask, request, redirect, url_for, abort, g
app = Flask(__name__)
templates = template.templates

# Page timer
# XXX: Seems buggy
#@app.before_request
#def before_request():
  #g.time_start = time.time()
#@app.after_request
#def after_request(response):
    #diff = int((time.time() - g.time_start) * 1000)  # to get a time in ms
    #if response.response and response.content_type.startswith("text/html") and response.status_code == 200:
        #response.response[0] = response.response[0].replace('__EXECUTION_TIME__', str(diff))
    #return response

@app.route("/")
def index():
    template = templates.get_template("index.html")
    return template.render(gigs=model.get_gig_calendar())

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
@app.route('/artist/')
def artist():
    template = templates.get_template("artist.html")
    return template.render(artists=model.get_artists())

@app.route('/artist/<int:id>/<name>')
@app.route('/artist/<int:id>/')
def artist_info(id, name=None):
    template = templates.get_template("artist_info.html")
    return template.render(artist=model.get_artist_by_id(id))

@app.route('/artist/add/', methods=['GET', 'POST'])
def artist_add():
    name = request.form.get('name')
    bio = request.form.get('bio')
    if name and bio:
        model.add_artist(name, bio)
        return redirect(url_for('artist'))
    else:
        template = templates.get_template("artist_add.html")
        return template.render()

@app.route('/artist/delete/', methods=['GET', 'POST'])
def artist_delete():
    id = request.form.get('id')
    if id:
        model.delete_artist(id)
        return redirect(url_for('artist'))
    else:
        template = templates.get_template("artist_delete.html")
        return template.render()

# Venues
@app.route('/venue/')
def venue():
    template = templates.get_template("venue.html")
    return template.render(venues=model.get_venues())

@app.route('/venue/<int:id>/<name>')
@app.route('/venue/<int:id>/')
def venue_info(id, name=None):
    template = templates.get_template("venue_info.html")
    return template.render(venue=model.get_venue_by_id(id))

@app.route('/venue/add/', methods=['GET', 'POST'])
def venue_add():
    name = request.form.get('name')
    address = request.form.get('address')
    if name:
        model.add_venue(name, address)
        return redirect(url_for('venue'))
    else:
        template = templates.get_template("venue_add.html")
        return template.render()

@app.route('/venue/delete/', methods=['GET', 'POST'])
def venue_delete():
    id = request.form.get('id')
    if id:
        model.delete_venue(id)
        return redirect(url_for('venue'))
    else:
        template = templates.get_template("venue_delete.html")
        return template.render()

# Gigs
@app.route('/gig/')
def gig():
    template = templates.get_template("gig.html")
    gigs=model.get_gigs()
    return template.render(gigdates=gigs)

@app.route('/gig/<int:id>')
def gig_info(id, name=None):
    template = templates.get_template("gig_info.html")
    return template.render(gig=model.get_gig_by_id(id))

@app.route('/gig/add/', methods=['GET', 'POST'])
def gig_add():
    if request.method == 'GET':
        template = templates.get_template("gig_add.html")
        return template.render()
    elif request.method == 'POST' and all([ i in request.form for i in ['date', 'time_hour', 'time_min', 'time_ampm', 'venue', 'artists']]):

        time_string = "{date} {time_hour}:{time_min} {time_ampm}".format(
                date=request.form['date'],
                time_hour=request.form['time_hour'],
                time_min=request.form['time_min'],
                time_ampm=request.form['time_ampm'])
        try:
            time_start = datetime.datetime.strptime(time_string, '%A %d %B, %Y %I:%M %p')
        except ValueError:
            print time_string
            # Invalid data for some reason
            abort(400)

        venue = model.get_venue_by_name(request.form.get('venue'))
        if not venue:
            model.add_venue(request.form.get('venue'))
        venue = model.get_venue_by_name(request.form.get('venue'))

        artist_ids = []
        for artist in request.form.getlist('artists'):
            if not artist: continue
            a = model.get_artist_by_name(artist)
            if a:
                artist_ids.append(a.id)
            else:
                model.add_artist(artist)
                a = model.get_artist_by_name(artist)
                artist_ids.append(a.id)

        model.add_gig(time_start, venue.id, artist_ids, name=request.form.get('name'))
        return redirect(url_for('gig'))
    else:
        abort(400)

@app.route('/gig/delete/', methods=['GET', 'POST'])
def gig_delete():
    id = request.form.get('id')
    if id:
        model.delete_gig(id)
        return redirect(url_for('gig'))
    else:
        template = templates.get_template("gig_delete.html")
        return template.render()

# Users
@app.route('/user/')
def user():
    template = templates.get_template("user.html")
    return template.render()
