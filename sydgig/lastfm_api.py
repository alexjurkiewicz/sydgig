from lib import lastfm

API_KEY = "2ed2ceec8bcde152af82eb77efd50eee"
API_SECRET = "7a10b0010b9a0490817b27ea3d315839"

api = lastfm.Api(API_KEY)

def get_artist_info(name):
    '''Given an artist name, return last.fm info about them'''
    try:
        artist = api.get_artist(name)
    except:
        artist = None
    return artist
