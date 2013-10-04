BROKER_URL = 'sqla+sqlite:///celerydb-tasks.sqlite'
BACKEND_URL = 'sqla+sqlite:///celerydb-results.sqlite'

import sydgig.lastfm_api as lastfm_api
import sydgig.googlemaps_api as googlemaps_api
import os, requests

from celery import Celery
from celery.utils.log import get_task_logger

logger = get_task_logger('tasks')

celery = Celery('tasks', broker=BROKER_URL, backend='database')
celery.conf.CELERY_RESULT_BACKEND = "database"
celery.conf.CELERY_RESULT_DBURI = "sqlite:///celerydb-results.sqlite"

# eg tasks.update_artist_data.delay('twerps')
@celery.task
def update_artist_data(name):
    '''Given the name of an artist in the database, clean up their record'''
    import sydgig.model as model
    original_record = model.get_artist_by_name(name)
    if original_record:
        info = lastfm_api.get_artist_info(name)

        name = info.name

        bio = info.bio.content

        imgdata = requests.get(info.image['mega'], stream=True).raw.read()
        imgext = info.image['mega'].rsplit('.', 1)[-1]
        localpath = os.path.join('sydgig', 'static', 'artist_images', str(original_record.id) + '.' + imgext)
        with open(localpath, 'wb') as f:
            f.write(imgdata)
        image_url = '/static/artist_images/' + str(original_record.id) + '.' + imgext

        model.update_artist_by_id(original_record.id, name=name, bio=bio, image_url=image_url)
    else:
        return "Couldn't update artist data for %s as no record matches that name!" % name

@celery.task
def update_venue_data(name):
    '''Given the name of a venue in the database, clean up its record'''
    import sydgig.model as model
    original_record = model.get_venue_by_name(name)
    if not original_record:
        return "Couldn't update venue data for %s as no record matches that name!" % name

    info = googlemaps_api.get_place_info(name)
    if info:
        address = info['formatted_address']
        model.update_venue_by_id(original_record.id, address=address)

@celery.task
def send_gig_report_email(recipient, sender, message):
    import smtplib
    s = smtplib.SMTP('localhost')
    s.sendmail(sender,  [recipient], message.as_string())
    s.quit()
