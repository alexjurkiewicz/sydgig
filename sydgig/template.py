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

def simpletime(value):
    '''datetime -> 8:30pm'''
    hr = str(int(value.strftime('%H'))) # strip any leading 0
    min = value.strftime('%M')
    if min == '00':
        return hr + value.strftime('%p').lower()
    else:
        return hr + ':' + min + value.strftime('%p').lower()
templates.filters['simpletime'] = simpletime

def simpledate(value):
    '''datetime -> Sat 3'''
    return value.strftime('%a ') + str(int(value.strftime('%d'))) # gets rid of leading 0
templates.filters['simpledate'] = simpledate

def longdate(value):
    '''datetime -> Friday 6 September, 2013'''
    return value.strftime('%A %d %B, %Y')
templates.filters['longdate'] = longdate

def truncate_list(l, maxitems=3, end='{num} more'):
    '''Return a list up to `maxitems` long with the last item as `end` if there were too many.
    `end` can use the format string {num} to get the number of truncated items.'''
    l = [i for i in l] # de-generator the input
    if len(l) > maxitems:
        return l[:maxitems] + [end.format(num=(len(l) - maxitems))]
    else:
        return l
templates.filters['truncate_list'] = truncate_list

def english_join(l, separator=', ', final_sep=' and '):
    l = [i for i in l]
    return separator.join(l[:-1]) + final_sep + l[-1]
templates.filters['english_join'] = english_join

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

