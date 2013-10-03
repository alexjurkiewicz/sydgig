from jinja2 import Environment, FileSystemLoader

import urllib, time, humanize, datetime

def guess_autoescape(template_name):
    if template_name is None or '.' not in template_name:
        return False
    ext = template_name.rsplit('.', 1)[1]
    return ext in ('html', 'htm', 'xml')

templates = Environment(loader=FileSystemLoader('sydgig/template/'),
                        autoescape=guess_autoescape,
                        extensions=['jinja2.ext.autoescape'])

# Filters
def quote_plus(value):
    return urllib.quote_plus(value)
templates.filters['quote_plus'] = quote_plus

def naturaltime(value):
    return humanize.naturaltime(value)
templates.filters['naturaltime'] = naturaltime

def simpledate(value):
    '''datetime -> Sat 3'''
    return value.strftime('%a ') + str(int(value.strftime('%d'))) # gets rid of leading 0
templates.filters['simpledate'] = simpledate

def longdate(value):
    '''datetime -> Friday 6 September, 2013'''
    return value.strftime('%A %d %B, %Y')
templates.filters['longdate'] = longdate

def truncate_list(l, maxitems=3, end='...'):
    '''Return a list of max length maxitems, with the last item as end if there were more in the first place'''
    l = [i for i in l] # de-generator the input
    if len(l) > maxitems:
        return l[:maxitems] + [end]
    else:
        return l
templates.filters['truncate_list'] = truncate_list

def istoday(d):
    '''return true if datetime d is the same day as today'''
    n = datetime.datetime.now()
    return d.year == n.year and d.month == n.month and d.day == n.day
templates.filters['istoday'] = istoday

# Global variables
def date_year():
    return int(time.strftime("%Y"))
def date_month():
    return time.strftime("%B")
def date_day():
    return int(time.strftime("%d")) # int() also strips the leading zero here
def date_today():
    n = datetime.datetime.now()
    return datetime.date(n.year, n.month, n.day)
templates.globals.update(date_year=date_year, date_month=date_month, date_day=date_day, date_today=date_today)

