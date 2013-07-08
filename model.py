import tasks

import database
from database import Artist, Gig, User, Venue

import sqlalchemy.orm

# Artists
def get_artists():
    return database.Session().query(Artist).all()

def get_artist_by_id(id):
    return database.Session().query(Artist).filter(Artist.id == id).one()

def get_artist_by_name(name):
    try:
        return database.Session().query(Artist).filter(Artist.name == name).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None

def add_artist(name, bio=None):
    s = database.Session()
    s.add(Artist(name, bio))
    s.commit()
    tasks.update_artist_data.delay(name)

def delete_artist(id):
    s = database.Session()
    artist = s.query(Artist).filter(Artist.id == id).one()
    s.delete(artist)
    s.commit()

def update_artist_by_id(id, name=None, bio=None):
    s = database.Session()
    artist = s.query(Artist).filter(Artist.id == id).one()
    if name:
        artist.name = name
    if bio:
        artist.bio = bio
    s.add(artist)
    s.commit()

# Gigs
def get_gigs():
    return database.Session().query(Gig).all()

def get_gig_by_id(id):
    return database.Session().query(Gig).filter(Gig.id == id).one()

def add_gig(time_start, venue_id, artist_ids):
    s = database.Session()
    gig = Gig(time_start, venue_id)
    for id in artist_ids:
        try:
            artist = s.query(Artist).filter(Artist.id == id).one()
            gig.performers.append(artist)
        except sqlalchemy.orm.exc.NoResultFound:
            pass
    s.add(gig)
    s.commit()

def delete_gig(id):
    s = database.Session()
    gig = s.query(Gig).filter(Gig.id == id).one()
    s.delete(gig)
    s.commit()

def add_artist_to_gig(gig_id, artist_id):
    s = database.Session()
    gig = s.query(Gig).filter(Gig.id == id).one()
    artist = s.query(Artist).filter(Artist.id == id).one()
    gig.performers.append(artist)
    s.add(gig)
    s.commit()

def delete_artist_from_gig(gig_id, artist_id):
    s = database.Session()
    gig = s.query(Gig).filter(Gig.id == id).one()
    artist = s.query(Artist).filter(Artist.id == id).one()
    idx = gig.performers.index(artist)
    del(gig.performers[idx])
    s.add(gig)
    s.commit()
        
def add_user_to_gig(gig_id, user_id):
    s = database.Session()
    gig = s.query(Gig).filter(Gig.id == id).one()
    user = s.query(User).filter(User.id == id).one()
    gig.attendees.append(user)
    s.add(gig)
    s.commit()

def delete_user_from_gig(gig_id, user_id):
    s = database.Session()
    gig = s.query(Gig).filter(Gig.id == id).one()
    user = s.query(User).filter(User.id == id).one()
    idx = gig.attendees.index(user)
    del(gig.performers[idx])
    s.add(gig)
    s.commit()

# Users
def get_users():
    return database.Session().query(User).all()

def get_user_by_id(id):
    return database.Session().query(User).filter(User.id == id).one()

def add_user(name):
    s = database.Session()
    s.add(User(name))
    s.commit()

def delete_user(id):
    s = database.Session()
    user = s.query(User).filter(User.id == id).one()
    s.delete(user)
    s.commit()

# Venues
def get_venues():
    return database.Session().query(Venue).all()

def get_venue_by_id(id):
    return database.Session().query(Venue).filter(Venue.id == id).one()

def get_venue_by_name(name):
    try:
        return database.Session().query(Venue).filter(Venue.name == name).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None

def add_venue(name, address):
    s = database.Session()
    s.add(Venue(name, address))
    s.commit()

def delete_venue(id):
    s = database.Session()
    venue = s.query(Venue).filter(Venue.id == id).one()
    s.delete(venue)
    s.commit()
