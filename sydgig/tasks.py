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
app.conf.CELERY_SEND_TASK_ERROR_EMAILS = (config.get('main', 'email_admin_to'), config.get('main', 'email_admin_to'))

# eg tasks.update_artist_data.delay('twerps')
@app.task
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
    import smtplib
    s = smtplib.SMTP('localhost')
    s.sendmail(sender,  [recipient], message.as_string())
    s.quit()

@app.task
def send_newsletter_signup_confirmation(recipient, verification_code):
    import smtplib, email
    sender_name = config.get('main', 'email_from_noreply_name')
    sender_email = config.get('main', 'email_from_noreply_email')
    message = email.mime.text.MIMEText('''Thanks for signing up to SydGig!
Please click on this link to verify your email: %s''' % ('http://www.sydgig.com/newsletter-verify?email=%s&code=%s' % (recipient, verification_code)))
    message['Subject'] = 'Welcome to SydGig'
    message['From'] = '%s <%s>' % (sender_name, sender_email)
    message['To'] = recipient
    s = smtplib.SMTP('localhost')
    s.sendmail(sender_email, [recipient], message.as_string())
    s.quit()

@app.task
def send_weekly_newsletter():
    import sydgig.model as model
    import time
    subscribers = model.get_all_newsletter_subscribers()
    sender_name = config.get('main', 'email_from_noreply_name')
    sender_email = config.get('main', 'email_from_noreply_email')
    gigs = model.get_gigs()

    subject = '''SydGig - upcoming gigs for {week_pretty}'''.format(week_pretty=time.strftime('%d %B %Y'))
    message_plain = ''
    message_plain += subject
    message_plain += '\n\n'
    for date in sorted(gigs.keys()):
        if gigs[date]:
            message_plain += '{date_pretty}:\n'.format(date_pretty=date.strftime('%a %d'))
            for gig in gigs[date]:
                artists = ', '.join([artist.name for artist in gig.performers])
                message_plain += '    - {artists} at {venue}\n'.format(artists=artists, venue=gig.venue.name)
            message_plain += '\n'

    print '''\nThat's all! Check out the website for any late additions or to submit gigs yourself: {website_url}\n\n'''.format(website_url=config.get('main', 'base_url_pretty'))
    print 'Regards, SydGig.\n'

assert 'send-weekly-newsletter' not in app.conf.CELERYBEAT_SCHEDULE
app.conf.CELERYBEAT_SCHEDULE['send-weekly-newsletter'] = { 'task': 'sydgig.tasks.send_weekly_newsletter', 'schedule': crontab(), }
# crontab(minute=0, hour=7, day_of_week=1, day_of_month='*', month_of_year='*')
