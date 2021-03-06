import sydgig.util as util

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, ForeignKey, Integer, String, DateTime, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///testdb.sqlite', echo=False)
Base = declarative_base()

gig_lineup = Table('gig_lineup', Base.metadata,
                       Column('gig_id', Integer, ForeignKey('gigs.id')),
                       Column('artist_id', Integer, ForeignKey('artists.id')),
                       )

class Artist(Base):
    __tablename__ = 'artists'
    id = Column(Integer, primary_key = True)
    name = Column(String, unique = True)
    bio = Column(String)
    image_url = Column(String)

    def __init__(self, name, bio=None):
        self.name = name
        self.bio = bio

    def __repr__(self):
        return u'{Artist %s: %s}' % (self.id, self.name)

    @property
    def name_slug(self):
        return util.slugify(self.name)

class Gig(Base):
    __tablename__ = 'gigs'
    __table_args__ = (
            UniqueConstraint('time_start', 'venue_id'),
            )
    id = Column(Integer, primary_key = True)
    time_start = Column(DateTime)
    venue_id = Column(Integer, ForeignKey('venues.id'))
    name = Column(String) # note: this is optional!
    description = Column(String) # also optional

    performers = relationship('Artist', secondary=gig_lineup, backref='gigs_performed')

    def __init__(self, time_start, venue_id, name=None, description=None):
        self.time_start = time_start
        self.venue_id = venue_id
        self.name = name
        self.description = description

    def __repr__(self):
        return '{Gig %s: %s: %s}' % (self.id, self.name if self.name else 'Untitled', ', '.join([i.name for i in self.performers]))

    @property
    def pretty_time_start(self):
        '''
        looks like: Thursday 26 September 2013, 04:21 pm
        We need to lowercase AM/PM from strftime
        '''
        return self.time_start.strftime('%A %d %B %Y, %I:%M ') + self.time_start.strftime('%p').lower()

class Venue(Base):
    __tablename__ = 'venues'
    id = Column(Integer, primary_key = True)
    name = Column(String, unique = True)
    address = Column(String)

    gigs_hosted = relationship("Gig", backref="venue")

    def __init__(self, name, address = None):
        self.name = name
        if address:
            self.address = address
        else:
            self.address = name

    def __repr__(self):
        return '{Venue %s: %s}' % (self.id, self.name)

    @property
    def name_slug(self):
        return util.slugify(self.name)

class NewsletterSubscriber(Base):
    __tablename__ = 'newslettersubscribers'
    id = Column(Integer, primary_key = True)
    email = Column(String, unique = True)
    verified = Column(Boolean)
    verification_code = Column(String)

    def __init__(self, email, verification_code):
        self.email = email
        self.verified = False
        self.verification_code = verification_code

    def __repr__(self):
        return '{Newsletter subscription %s: %s}' % (self.id, self.name)

#class ArtistURL(Base):
    #__tablename__ = 'artisturls'
    #id = Column(Integer, primary_key = True)
    #url = Column(String)
    #description = Column(String)
    #artist_id = Column(Integer, ForeignKey('artists.id'))

Base.metadata.create_all(engine) 
Session = sessionmaker(bind=engine)
session = Session()

