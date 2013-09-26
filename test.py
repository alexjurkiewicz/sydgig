import sydgig.model as model

import random, string, datetime

N_RANDOM_ARTISTS = 20
N_RANDOM_VENUES = 5
N_RANDOM_GIGS = 32

def random_artist():
    return "The %ss" % (''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(random.randint(4, 7))).title())
def random_venue():
    return "The %s Hotel" % (''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(random.randint(4, 7))).title())

print "Adding %s random artists..." % N_RANDOM_ARTISTS
for i in range(N_RANDOM_ARTISTS):
    model.add_artist(random_artist(), 'No bio available')
print "Adding %s random venues..." % N_RANDOM_VENUES
for i in range(N_RANDOM_VENUES):
    model.add_venue(random_venue())
print "Adding %s random gigs in the next 14 days..." % N_RANDOM_GIGS
for i in range(N_RANDOM_GIGS):
    artists = random.sample(model.get_artists(), random.randint(2, 5))
    venue = random.choice(model.get_venues())
    model.add_gig(time_start = datetime.datetime.now() + datetime.timedelta(days=random.randint(0,14)), venue_id = venue.id, artist_ids = [artist.id for artist in artists], name="%s album launch" % (artists[0].name))
