from __future__ import division, absolute_import

import datetime

from flask import Flask, request, redirect, url_for
app = Flask(__name__)

from template import templates
import controller

@app.route("/")
def index():
    template = templates.get_template("index.html")
    return template.render()

# Artists
@app.route('/artist/')
def artist():
    template = templates.get_template("artist.html")
    return template.render(artists=controller.get_artists())

@app.route('/artist/<int:id>/<name>')
@app.route('/artist/<int:id>/')
def artist_info(id, name=None):
    template = templates.get_template("artist_info.html")
    return template.render(artist=controller.get_artist_by_id(id))

@app.route('/artist/add/', methods=['GET', 'POST'])
def artist_add():
    name = request.form.get('name')
    bio = request.form.get('bio')
    if name and bio:
        controller.add_artist(name, bio)
        return redirect(url_for('artist'))
    else:
        template = templates.get_template("artist_add.html")
        return template.render()

@app.route('/artist/delete/', methods=['GET', 'POST'])
def artist_delete():
    id = request.form.get('id')
    if id:
        controller.delete_artist(id)
        return redirect(url_for('artist'))
    else:
        template = templates.get_template("artist_delete.html")
        return template.render()

# Venues
@app.route('/venue/')
def venue():
    template = templates.get_template("venue.html")
    return template.render(venues=controller.get_venues())

@app.route('/venue/<int:id>/<name>')
@app.route('/venue/<int:id>/')
def venue_info(id, name=None):
    return repr(controller.get_venue_by_id(id))

@app.route('/venue/add/', methods=['GET', 'POST'])
def venue_add():
    name = request.form.get('name')
    address = request.form.get('address')
    if name and address:
        controller.add_venue(name, address)
        return redirect(url_for('venue'))
    else:
        template = templates.get_template("venue_add.html")
        return template.render()

@app.route('/venue/delete/', methods=['GET', 'POST'])
def venue_delete():
    id = request.form.get('id')
    if id:
        controller.delete_venue(id)
        return redirect(url_for('venue'))
    else:
        template = templates.get_template("venue_delete.html")
        return template.render()

# Gigs
@app.route('/gig/')
def gig():
    template = templates.get_template("gig.html")
    return template.render(gigs=controller.get_gigs())

@app.route('/gig/<int:id>')
def gig_info(id, name=None):
    return repr(controller.get_gig_by_id(id))

@app.route('/gig/add/', methods=['GET', 'POST'])
def gig_add():
    if 'time_start' in request.form and 'venue' in request.form and 'artists' in request.form:
        time_start = datetime.datetime.strptime(request.form.get('time_start'), '%Y-%m-%d %H:%M')
        venue = controller.get_venue_by_name(request.form.get('venue'))
        if not venue:
            controller.add_venue(request.form.get('venue'), 'Unknown')
        venue = controller.get_venue_by_name(request.form.get('venue'))
        artist_ids = []
        for artist in request.form.getlist('artists'):
            a = controller.get_artist_by_name(artist)
            if a:
                artist_ids.append(a.id)
            else:
                controller.add_artist(artist)
                a = controller.get_artist_by_name(artist)
                artist_ids.append(a.id)
        controller.add_gig(time_start, venue.id, artist_ids)
        return redirect(url_for('gig'))
    else:
        template = templates.get_template("gig_add.html")
        return template.render()

@app.route('/gig/delete/', methods=['GET', 'POST'])
def gig_delete():
    id = request.form.get('id')
    if id:
        controller.delete_gig(id)
        return redirect(url_for('gig'))
    else:
        template = templates.get_template("gig_delete.html")
        return template.render()

# Users
@app.route('/user/')
def user():
    template = templates.get_template("user.html")
    return template.render()

if __name__ == "__main__":
    app.run(debug=True)
