BROKER_URL = 'sqla+sqlite:///celerydb-tasks.sqlite'
BACKEND_URL = 'sqla+sqlite:///celerydb-results.sqlite'

import sydgig.lastfm_api as lastfm_api
import sydgig.googlemaps_api as googlemaps_api
import sydgig.config as config
import os, requests

from celery import Celery
from celery.utils.log import get_task_logger
from celery.task import periodic_task
from celery.schedules import crontab


logger = get_task_logger('tasks')

app = Celery('tasks', broker=BROKER_URL, backend='database')
app.conf.CELERY_RESULT_BACKEND = "database"
app.conf.CELERY_RESULT_DBURI = "sqlite:///celerydb-results.sqlite"
app.conf.CELERY_TIMEZONE = config.get('main', 'timezone')
app.conf.CELERY_SEND_TASK_ERROR_EMAILS = True
app.conf.ADMINS = ((config.get('main', 'email_admin_to'), config.get('main', 'email_admin_to')),)
app.conf.EMAIL_HOST = config.get('main', 'smtp_server')
app.conf.SERVER_EMAIL = config.get('main', 'email_from_noreply_email')

# low scalability = easier debugging
app.conf.CELERYD_CONCURRENCY = config.get('main', 'celery_workers')
app.conf.CELERYD_PREFETCH_MULTIPLIER = 1
app.conf.BROKER_POOL_LIMIT = None
app.conf.CELERYD_MAX_TASKS_PER_CHILD = 1

# eg tasks.update_artist_data.delay('twerps')
@app.task
def update_artist_data(name):
    '''Given the name of an artist in the database, clean up their record'''
    import sydgig.model as model
    original_record = model.get_artist_by_name(name)
    if original_record:
        info = lastfm_api.get_artist_info(name)
        if not info: # last.fm has nothing
            return "last.fm has no info on artist '%s'" % name
        name = info.name
        bio = info.bio.content

        mega_url = info.image['mega']
        if mega_url:
            imgdata = requests.get(mega_url, stream=True).raw.read()
            imgext = mega_url.rsplit('.', 1)[-1]
            localpath = os.path.join('sydgig', 'static', 'artist_images', str(original_record.id) + '.' + imgext)
            with open(localpath, 'wb') as f:
                f.write(imgdata)
            image_url = '/static/artist_images/' + str(original_record.id) + '.' + imgext
        else:
            image_url='/static/artist_images/unknown.png'

        model.update_artist_by_id(original_record.id, name=name, bio=bio, image_url=image_url)
    else:
        return "Couldn't update artist data for %s as no record matches that name!" % name

@app.task
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

@app.task
def send_gig_report_email(recipient, sender, message):
    send_email.delay(sender, recipient, message.as_string())

@app.task
def send_newsletter_signup_confirmation(recipient, verification_code):
    import email
    sender_name = config.get('main', 'email_from_noreply_name')
    sender_email = config.get('main', 'email_from_noreply_email')
    message = email.mime.text.MIMEText('''Thanks for signing up to SydGig!
Please click on this link to verify your email: %s''' % ('http://www.sydgig.com/newsletter-verify?email=%s&code=%s' % (recipient, verification_code)))
    message['Subject'] = 'Welcome to SydGig'
    message['From'] = '%s <%s>' % (sender_name, sender_email)
    message['To'] = recipient
    send_email.delay(sender_email, recipient, message.as_string())

@app.task
def send_weekly_newsletter():
    import sydgig.model as model
    import time, email
    subscribers = model.get_all_newsletter_subscribers()
    sender_name = config.get('main', 'email_from_noreply_name')
    sender_email = config.get('main', 'email_from_noreply_email')
    gigs = model.get_gigs()

    subject = '''SydGig - upcoming gigs for {week_pretty}'''.format(week_pretty=time.strftime('%d %B %Y'))
    message_plain = ''
    for date in sorted(gigs.keys()):
        if gigs[date]:
            date_pretty = date.strftime('%A') + ' ' + str(int(date.strftime('%d')))
            message_plain += '{date_pretty}:\n'.format(date_pretty=date_pretty)
            for gig in gigs[date]:
                artists = ', '.join([artist.name for artist in gig.performers])
                gig_url =  config.get('main', 'base_url_pretty') + '/gig/%s' % gig.id
                message_plain += '    - {artists} at {venue}: {gig_url}\n'.format(artists=artists, venue=gig.venue.name, gig_url=gig_url)
            message_plain += '\n'

    message_plain += '''\nThat's all! Check out the website for late additions and to submit gigs yourself: {website_url}\n\n'''.format(website_url=config.get('main', 'base_url_pretty'))
    message_plain += 'Regards, SydGig.\n'

    message = email.mime.text.MIMEText(message_plain)
    message['Subject'] = subject
    message['From'] = '%s <%s>' % (sender_name, sender_email)
    for recipient in subscribers:
        message['To'] = recipient
        send_email.delay(sender_email, recipient, message.as_string())

assert 'send-weekly-newsletter' not in app.conf.CELERYBEAT_SCHEDULE
app.conf.CELERYBEAT_SCHEDULE['send-weekly-newsletter'] = { 'task': 'sydgig.tasks.send_weekly_newsletter', 'schedule': crontab(minute=0, hour=7, day_of_week=1, day_of_month='*', month_of_year='*'), }

@app.task
def send_email(sender, recipient, body_text):
    import smtplib
    s = smtplib.SMTP(config.get('main', 'smtp_server'))
    s.sendmail(sender, [recipient], body_text)

@app.task
def send_admin_notification(subject, body_text):
    import email
    message = email.mime.text.MIMEText(body_text)
    message['Subject'] = subject
    message['From'] = '%s <%s>' % (config.get('main', 'email_from_noreply_name'), config.get('main', 'email_from_noreply_email'))
    send_email(config.get('main', 'email_from_noreply_email'), config.get('main', 'email_admin_to'), message.as_string())
