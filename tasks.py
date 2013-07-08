BROKER_URL = 'sqla+sqlite:///celerydb-tasks.sqlite'
BACKEND_URL = 'sqla+sqlite:///celerydb-results.sqlite'

import model, lastfm_api
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
    original_record = model.get_artist_by_name(name)
    if original_record:
        info = lastfm_api.get_artist_info(name)

        name = info.name

        bio = info.bio.content

        imgdata = requests.get(info.image['mega'], stream=True).raw.read()
        imgext = info.image['mega'].rsplit('.', 1)[-1]
        localpath = os.path.join('static', 'artist_images', str(original_record.id) + '.' + imgext)
        with open(localpath, 'wb') as f:
            f.write(imgdata)
        image_url = '/static/artist_images/' + str(original_record.id) + '.' + imgext

        model.update_artist_by_id(original_record.id, name=name, bio=bio, image_url=image_url)
    else:
        return "Couldn't update artist data for %s as no record matches that name!" % name

@celery.task
def test():
    print os.getcwd()
