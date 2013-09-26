import datetime

import sydgig.tasks as tasks
import sydgig.database as database
from sydgig.database import Artist, Gig, User, Venue

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

def update_artist_by_id(id, name=None, bio=None, image_url=None):
    s = database.Session()
    artist = s.query(Artist).filter(Artist.id == id).one()
    if name:
        artist.name = name
    if bio:
        artist.bio = bio
    if image_url:
        artist.image_url = image_url
    s.add(artist)
    s.commit()

# Gigs
def get_gigs(days_into_future=7, days_into_past=0):
    '''Get all gigs matching the specified conditions. Today's gigs are always returned.
    Time of day isn't taken into account (a search at 9pm will include gigs that started at 8pm)'''
    # Generate datetime.datetime objects at the 00:00 of start day and 23:59 of end day
    now = datetime.datetime.now()
    start_time = now - datetime.timedelta(days=days_into_past)
    end_time = now + datetime.timedelta(days=days_into_future)
    start_day = datetime.datetime(start_time.year, start_time.month, start_time.day, 0, 0)
    end_day = datetime.datetime(end_time.year, end_time.month, end_time.day, 23, 59)

    giglist = database.Session().query(Gig).filter(Gig.time_start >= start_day, Gig.time_start <= end_day).all()
    gigs = {}
    # Pre-populate keys for all dates in the given interval
    i = start_day
    while i < end_day:
        gigs[datetime.date(i.year, i.month, i.day)] = []
        i = i + datetime.timedelta(days=1)
    # Add all gigs
    for gig in giglist:
        time = gig.time_start
        date = datetime.date(time.year, time.month, time.day)
        gigs[date].append(gig)
    return gigs

def get_gig_by_id(id):
    return database.Session().query(Gig).filter(Gig.id == id).one()

def get_gig_calendar(weeks=4):
    '''Return gigs starting from the most recent Monday for the next `weeks` weeks.'''
    now = datetime.datetime.now()
    #start_time = now - datetime.timedelta(days=now.weekday)
    #start_time = datetime.datetime(start_time.year, start_time.month, start_time.day, 0, 0)
    #end_time = now + datetime.timedelta(weeks=weeks, days=(6-now.weekday))
    #end_time = datetime.datetime(end_time.year, end_time.month, end_time.day, 23, 59)
    previous_days = now.weekday()
    future_days = (7 * weeks) + (6 - now.weekday())
    return get_gigs(days_into_future=future_days, days_into_past=previous_days)


def add_gig(time_start, venue_id, artist_ids, name=None):
    s = database.Session()
    gig = Gig(time_start, venue_id, name=name)
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

def add_venue(name, address=None):
    s = database.Session()
    s.add(Venue(name, address))
    s.commit()
    if address in [None, u'']:
        tasks.update_venue_data.delay(name)

def delete_venue(id):
    s = database.Session()
    venue = s.query(Venue).filter(Venue.id == id).one()
    s.delete(venue)
    s.commit()

def update_venue_by_id(id, name=None, address=None):
    s = database.Session()
    venue = s.query(Venue).filter(Venue.id == id).one()
    if name:
        venue.name = name
    if address:
        venue.address = address
    s.add(venue)
    s.commit()
