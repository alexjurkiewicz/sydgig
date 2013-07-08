BROKER_URL = 'sqla+sqlite:///celerydb-tasks.sqlite'
BACKEND_URL = 'sqla+sqlite:///celerydb-results.sqlite'

import model, lastfm_api

from celery import Celery
from celery.utils.log import get_task_logger

logger = get_task_logger('tasks')

celery = Celery('tasks', broker=BROKER_URL, backend='database')
celery.conf.CELERY_RESULT_BACKEND = "database"
celery.conf.CELERY_RESULT_DBURI = "sqlite:///celerydb-results.sqlite"

# eg tasks.update_artist_data.delay('twerps')
@celery.task
def update_artist_data(name):
    original_record = model.get_artist_by_name(name)
    if original_record:
        info = lastfm_api.get_artist_info(name)
        model.update_artist_by_id(original_record.id, name=info.name, bio=info.bio.content)
    else:
        return "Couldn't update artist data for %s as no record matches that name!" % name
