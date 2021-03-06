from __future__ import division, absolute_import

import datetime, random, time, os, smtplib, email
import logging.handlers

import sydgig.template as template
import sydgig.model as model
import sydgig.tasks as tasks
import sydgig.config as config


from flask import Flask, request, redirect, url_for, abort, g
import werkzeug

import recaptcha.client.captcha as recaptcha

app = Flask(__name__)
app.config['SECRET_KEY'] = config.get('main', 'app_secret_key')
app.config['DEBUG'] = config.get('main', 'debug')

# All error logs are emailed
mail_handler = logging.handlers.SMTPHandler(config.get('main', 'smtp_server'), config.get('main', 'email_from_noreply_email'), [config.get('main', 'email_admin_to')], 'SydGig failure')
mail_handler.setLevel(logging.ERROR)
app.logger.addHandler(mail_handler)

RECAPTCHA_PUBLIC_KEY = config.get('main', 'recaptcha_public_key')
RECAPTCHA_PRIVATE_KEY = config.get('main', 'recaptcha_private_key')
EMAIL_FROM_NOREPLY_NAME = config.get('main', 'email_from_noreply_name')
EMAIL_FROM_NOREPLY_EMAIL = config.get('main', 'email_from_noreply_email')
EMAIL_ADMIN_TO = config.get('main', 'email_admin_to')

templates = template.templates

# Page timer
@app.before_request
def before_request():
  g.time_start = time.time()
@app.after_request
def after_request(response):
    diff = int((time.time() - g.time_start) * 1000)  # to get a time in ms
    if response.response and not isinstance(response.response, werkzeug.wsgi.ClosingIterator) and \
       response.content_type.startswith("text/html"):
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
    return response, 404

@app.errorhandler(500)
def page_not_found(e):
    template = templates.get_template("500.html")
    response = template.render()
    return response, 500

@app.errorhandler(400)
def bad_request(e):
    template = templates.get_template("400.html")
    response = template.render()
    return response, 400

@app.route('/about')
def about():
    vids = ( 'http://www.youtube.com/watch?v=M8XmoroZ3zo', # preatures - is this how you feel
            'http://www.youtube.com/watch?v=yBL3aKLZ6qY', # coach bombay - take off
            'http://www.youtube.com/watch?v=ED6yVA_zw7A', # client liaison @ golden plains
            'http://www.youtube.com/watch?v=ic1DjIFDbeQ', # the presets - fall
            'http://www.youtube.com/watch?v=yfEmJPMVWuo', # collarbones - teenage dreams
            'http://www.youtube.com/watch?v=Vfl18wIVApQ', # standish/carlyon - nono/yoyo
            'http://www.youtube.com/watch?v=Cc9ScFgWqcg', # single twin - my silken tooth
            'http://www.youtube.com/watch?v=enZ-TZrwLPY', # los tones - buchanan hammer
            'http://www.youtube.com/watch?v=tb_Ogb0zzhA', # hermitude - speak of the devil
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

# Edit gig
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    template = templates.get_template("gig_edit.html")
    gig = model.get_gig_by_id(id)
    captcha_html=recaptcha.displayhtml(RECAPTCHA_PUBLIC_KEY)
    return template.render(gig=gig, captcha_html=captcha_html)

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
        msg['From'] = '%s <%s>' % (EMAIL_FROM_NOREPLY_NAME, EMAIL_FROM_NOREPLY_EMAIL)
        msg['To'] = EMAIL_ADMIN_TO

        tasks.send_gig_report_email.delay(sender=EMAIL_FROM_NOREPLY_EMAIL, recipient=EMAIL_ADMIN_TO, message=msg)

        template = templates.get_template("gig_report_success.html")
        return template.render(gig=model.get_gig_by_id(id))
    else:
        assert False

# Submit new gig
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        template = templates.get_template("add.html")
        return template.render(captcha_html=recaptcha.displayhtml(RECAPTCHA_PUBLIC_KEY))
    elif request.method == 'POST':
        # validate captcha
        recaptcha_response = recaptcha.submit(request.form['recaptcha_challenge_field'], request.form['recaptcha_response_field'], RECAPTCHA_PRIVATE_KEY, request.remote_addr)
        if not recaptcha_response.is_valid:
            template = templates.get_template("recaptcha_failed.html")
            return template.render()

        time_start = time.strptime("%s %s" % (request.form['date'], request.form['time']), '%A %d %B, %Y %H:%M')
        time_start = datetime.datetime.fromtimestamp(time.mktime(time_start))
        venue = request.form['venue']
        artists = [artist for artist in request.form.getlist('artists')if artist]
        gigname = request.form['gigname']
        gigdesc = request.form['gigdesc']
        if not venue or not artists:
            abort(400)

        if not model.get_venue_by_name(venue):
            model.add_venue(venue)
        venue_id = model.get_venue_by_name(venue).id
        for artist in artists:
            if not model.get_artist_by_name(artist):
                model.add_artist(artist)
        artist_ids = [model.get_artist_by_name(artist).id for artist in artists]
        gig_id = model.add_gig(time_start, venue_id, artist_ids, name=gigname, description = gigdesc)

        return redirect('/gig/%s' % gig_id)
    else: # unknown request method
        assert False

# Newsletter signup
@app.route('/newsletter-signup', methods=['POST'])
def newsletter_signup():
    email = request.form['email']
    if util.verify_email(email):
        model.subscribe_email(email)
        template = templates.get_template("newsletter_signup.html")
        return template.render()
    else:
        abort(400)

@app.route('/newsletter-verify')
def newsletter_verify():
    email = request.args['email']
    code = request.args['code']
    if model.verify_email(email, code):
        template = templates.get_template("newsletter_verify_success.html")
    else:
        template = templates.get_template("newsletter_verify_failure.html")
    return template.render()
