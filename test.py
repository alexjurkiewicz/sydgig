import sydgig.model as model

import random, string, datetime, time

N_RANDOM_ARTISTS = 20
N_RANDOM_VENUES = 5
N_RANDOM_GIGS = 32
N_FUTURE_GIG_DAYS = 30

VOWELS='aeiuo'
CONSONANTS='bcdfghjklmnpqrstvwxyz'

def random_artist():
    return "The %ss" % (''.join(
        random.choice(
            random.choice([VOWELS, CONSONANTS])
        ) for x in range(random.randint(4, 7))).title())

def random_venue():
    return "The %s Hotel" % (''.join(random.choice(string.ascii_lowercase) for x in range(random.randint(4, 7))).title())

def random_start_time():
    t = random.choice(['20:30pm', '16:00pm', '22:00', '21:00'])
    d = datetime.datetime.now() + datetime.timedelta(days=random.randint(0,N_FUTURE_GIG_DAYS))
    structtime = time.strptime(t + ' ' + d.strftime('%d-%m-%Y'), '%H:%M %d-%m-%Y')
    return datetime.datetime.fromtimestamp(time.mktime(structtime))

if __name__ == '__main__':
    print "Adding %s random artists..." % N_RANDOM_ARTISTS
    for i in range(N_RANDOM_ARTISTS):
        model.add_artist(random_artist(), 'No bio available')
    print "Adding %s random venues..." % N_RANDOM_VENUES
    for i in range(N_RANDOM_VENUES):
        model.add_venue(random_venue())
    print "Adding %s random gigs in the next %s days..." % (N_RANDOM_GIGS, N_FUTURE_GIG_DAYS)
    for i in range(N_RANDOM_GIGS):
        artists = random.sample(model.get_artists(), random.randint(2, 5))
        venue = random.choice(model.get_venues())

        try:
            model.add_gig(
                time_start = random_start_time(),
                venue_id = venue.id,
                artist_ids = [artist.id for artist in artists], name="%s album launch" % (artists[0].name)
            )
        except:
            print "Couldn't add a gig (probably a start time collision)"
