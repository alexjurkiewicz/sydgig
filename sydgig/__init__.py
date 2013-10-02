from __future__ import division, absolute_import

import datetime, random, time, os, smtplib, email

import sydgig.template as template
import sydgig.model as model

from flask import Flask, request, redirect, url_for, abort, g

import recaptcha.client.captcha as recaptcha

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)

RECAPTCHA_PUBLIC_KEY = '6LdSPugSAAAAAJncStVRJ_9FNY-lJ85QKKXWDDBd'
RECAPTCHA_PRIVATE_KEY = '6LdSPugSAAAAAGq-KLr2Pv4rDeABYBqwEr2UO1Mo'
EMAIL_ADMIN_FROM = 'sydgig@sydgig.com'
EMAIL_ADMIN_TO = 'alex@jurkiewi.cz'

templates = template.templates

# Page timer
@app.before_request
def before_request():
  g.time_start = time.time()
@app.after_request
def after_request(response):
    diff = int((time.time() - g.time_start) * 1000)  # to get a time in ms
    if response.response and response.content_type.startswith("text/html") and response.status_code == 200:
        response.response[0] = response.response[0].replace('__EXECUTION_TIME__', str(diff))
        response.headers["content-length"] = len(response.response[0])
    return response

@app.route("/")
def index():
    template = templates.get_template("index.html")
    return template.render(gigs=model.get_gig_calendar())

@app.errorhandler(404)
def page_not_found(e):
    template = templates.get_template("404.html")
    response = template.render()
    # after_request handlers aren't run with the error handler, so calculate generation time here
    diff = int((time.time() - g.time_start) * 1000)  # to get a time in ms
    response = response.replace('__EXECUTION_TIME__', str(diff))
    return response, 404

@app.errorhandler(500)
def page_not_found(e):
    template = templates.get_template("500.html")
    response = template.render()
    # after_request handlers aren't run with the error handler, so calculate generation time here
    diff = int((time.time() - g.time_start) * 1000)  # to get a time in ms
    response = response.replace('__EXECUTION_TIME__', str(diff))
    return response, 500

@app.errorhandler(400)
def bad_request(e):
    template = templates.get_template("400.html")
    response = template.render()
    # after_request handlers aren't run with the error handler, so calculate generation time here
    diff = int((time.time() - g.time_start) * 1000)  # to get a time in ms
    response = response.replace('__EXECUTION_TIME__', str(diff))
    return response, 400

@app.route('/about')
def about():
    vids = ( 'http://www.youtube.com/watch?v=M8XmoroZ3zo', # preatures - is this how you feel
            'http://www.youtube.com/watch?v=yBL3aKLZ6qY', # coach bombay - take off
            'http://www.youtube.com/watch?v=ED6yVA_zw7A', # client liaison @ golden plains
            'http://www.youtube.com/watch&v=ic1DjIFDbeQ', # the presets - fall
            )
    template = templates.get_template("about.html")
    return template.render(video=random.choice(vids))

# Artists
@app.route('/artist/<int:id>/<name>')
@app.route('/artist/<int:id>/')
def artist_info(id, name=None):
    template = templates.get_template("artist_info.html")
    return template.render(artist=model.get_artist_by_id(id))

# Venues
@app.route('/venue/<int:id>/<name>')
@app.route('/venue/<int:id>/')
def venue_info(id, name=None):
    template = templates.get_template("venue_info.html")
    return template.render(venue=model.get_venue_by_id(id))

# Gigs
@app.route('/gig/<int:id>')
def gig_info(id):
    template = templates.get_template("gig_info.html")
    return template.render(gig=model.get_gig_by_id(id))

@app.route('/gig/report/<int:id>', methods=('GET', 'POST'))
def gig_report(id):
    if request.method == 'GET':
        template = templates.get_template("gig_report.html")
        return template.render(gig=model.get_gig_by_id(id), captcha_html=recaptcha.displayhtml(RECAPTCHA_PUBLIC_KEY))
    elif request.method == 'POST':
        print "hello"
        # validate captcha
        recaptcha_response = recaptcha.submit(request.form['recaptcha_challenge_field'], request.form['recaptcha_response_field'], RECAPTCHA_PRIVATE_KEY, request.remote_addr)
        if not recaptcha_response.is_valid:
            abort(400)
        msg = email.mime.text.MIMEText('Gig ID: %s\nReason: %s\nFrom IP: %s' % (id, request.form['reason'], request.remote_addr))
        msg['Subject'] = 'Sydgig report for gig %s' % id
        msg['From'] = EMAIL_ADMIN_FROM
        msg['To'] = EMAIL_ADMIN_TO
        try:
            s = smtplib.SMTP('localhost')
            s.sendmail(EMAIL_ADMIN_FROM,  [EMAIL_ADMIN_TO], msg.as_string())
            s.quit()
        except BaseException as e:
            print "Couldn't send email report (%s)" % e
            print "Message as follows:"
            print msg.as_string()

        template = templates.get_template("gig_report_success.html")
        return template.render(gig=model.get_gig_by_id(id))
    else:
        assert False

# Submit
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'GET':
        template = templates.get_template("submit.html")
        return template.render(captcha_html=recaptcha.displayhtml(RECAPTCHA_PUBLIC_KEY))
    elif request.method == 'POST':
        # validate captcha
        recaptcha_response = recaptcha.submit(request.form['recaptcha_challenge_field'], request.form['recaptcha_response_field'], RECAPTCHA_PRIVATE_KEY, request.remote_addr)
        if not recaptcha_response.is_valid:
            abort(400)

        time_start = time.strptime("%s %s" % (request.form['date'], request.form['time']), '%A %d %B, %Y %H:%M')
        time_start = datetime.datetime.fromtimestamp(time.mktime(time_start))
        venue = request.form['venue']
        artists = request.form.getlist('artists')
        gigname = request.form['gigname']
        if not venue or not artists:
            abort(400)

        if not model.get_venue_by_name(venue):
            model.add_venue(venue)
        venue_id = model.get_venue_by_name(venue).id
        for artist in artists:
            if not model.get_artist_by_name(artist):
                model.add_artist(artist)
        artist_ids = [model.get_artist_by_name(artist).id for artist in artists]
        model.add_gig(time_start, venue_id, artist_ids, name=gigname)

        return redirect(url_for('index'))
    else: # unknown request method
        assert False
