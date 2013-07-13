import requests, json, urllib

API_KEY = 'AIzaSyA_z7C_7-ZzrMYDcJisKI6GrukMdFdxn3M'
LOCATION = urllib.quote_plus('-33.867387,151.207629') # sydney, according to something i found on the internet
BASE_URL = 'https://maps.googleapis.com/maps/api/place/textsearch/json?sensor=false&key={apikey}&location={location}&radius=50000'

def get_place_info(name):
    '''Try to find an address for a given place name'''
    url = BASE_URL.format(apikey=API_KEY, location=LOCATION) + '&query=%s' % urllib.quote_plus(name)
    r = requests.get(url)
    data = json.loads(r.text)
    if data['status'] == u'OK':
        return data['results'][0]
    else:
        return None
