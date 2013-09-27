from jinja2 import Environment, FileSystemLoader

import urllib, time, humanize, datetime

def guess_autoescape(template_name):
    if template_name is None or '.' not in template_name:
        return False
    ext = template_name.rsplit('.', 1)[1]
    return ext in ('html', 'htm', 'xml')

def quote_plus(value):
    return urllib.quote_plus(value)

def naturaltime(value):
    return humanize.naturaltime(value)

def simpledate(value):
    '''datetime -> Sat 3'''
    return value.strftime('%a ') + str(int(value.strftime('%d'))) # gets rid of leading 0

def longdate(value):
    '''datetime -> Friday 6 September, 2013'''
    print value
    return value.strftime('%A %d %B, %Y')

templates = Environment(loader=FileSystemLoader('sydgig/template/'),
                        autoescape=guess_autoescape,
                        extensions=['jinja2.ext.autoescape'])

templates.filters['quote_plus'] = quote_plus
templates.filters['naturaltime'] = naturaltime
templates.filters['simpledate'] = simpledate
templates.filters['longdate'] = longdate
def date_year():
    return int(time.strftime("%Y"))
def date_month():
    return time.strftime("%B")
def date_day():
    return int(time.strftime("%d")) # int() also strips the leading zero here
def date_today():
    n = datetime.datetime.now()
    #return datetime.datetime(n.year, n.month, n.day, 0, 0)
    return datetime.date(n.year, n.month, n.day)
def istoday(d):
    '''return true if datetime d is the same day as today'''
    n = datetime.datetime.now()
    return d.year == n.year and d.month == n.month and d.day == n.day
templates.globals.update(date_year=date_year, date_month=date_month, date_day=date_day, date_today=date_today, istoday=istoday)

