from sqlalchemy import create_engine
from sqlalchemy import Table, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///testdb.sqlite', echo=True)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

gig_lineup = Table('gig_lineup', Base.metadata,
                       Column('gig_id', Integer, ForeignKey('gigs.id')),
                       Column('artist_id', Integer, ForeignKey('artists.id')),
                       )

gig_attendance = Table('gig_attendance', Base.metadata,
                       Column('gig_id', Integer, ForeignKey('gigs.id')),
                       Column('user_id', Integer, ForeignKey('users.id')),
                       )

class Artist(Base):
    __tablename__ = 'artists'
    id = Column(Integer, primary_key = True)
    name = Column(String, unique = True)
    bio = Column(String)

    def __init__(self, name, bio):
        self.name = name
        self.bio = bio

    def __repr__(self):
        return '{Artist %s: %s}' % (self.id, self.name)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key = True)
    name = Column(String)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '{User %s: %s}' % (self.id, self.name)

class Gig(Base):
    __tablename__ = 'gigs'
    id = Column(Integer, primary_key = True)
    time_start = Column(DateTime)
    venue_id = Column(Integer, ForeignKey('venues.id'))

    performers = relationship('Artist', secondary=gig_lineup, backref='gigs_performed')
    attendees = relationship('User', secondary=gig_attendance, backref='gigs_attended')

    def __init__(self, time_start, venue_id):
        self.time_start = time_start
        self.venue_id = venue_id

    def __repr__(self):
        return '{Gig %s}' % (self.id)

class Venue(Base):
    __tablename__ = 'venues'
    id = Column(Integer, primary_key = True)
    name = Column(String, unique = True)
    address = Column(String)

    gigs_hosted = relationship("Gig", backref="venue")

    def __init__(self, name, address = None):
        self.name = name
        self.address = address

    def __repr__(self):
        return '{Venue %s: %s}' % (self.id, self.name)

Base.metadata.create_all(engine) 
Session = sessionmaker(bind=engine)
session = Session()

