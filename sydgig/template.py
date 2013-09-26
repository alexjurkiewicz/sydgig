from jinja2 import Environment, FileSystemLoader

import urllib, time, humanize

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
    '''datetime -> 07/03'''
    return value.strftime('%d/%m')

templates = Environment(loader=FileSystemLoader('sydgig/template/'),
                        autoescape=guess_autoescape,
                        extensions=['jinja2.ext.autoescape'])

templates.filters['quote_plus'] = quote_plus
templates.filters['naturaltime'] = naturaltime
templates.filters['simpledate'] = simpledate
def date_year():
    return int(time.strftime("%Y"))
def date_month():
    return time.strftime("%B")
def date_day():
    return int(time.strftime("%d")) # int() also strips the leading zero here
templates.globals.update(date_year=date_year, date_month=date_month, date_day=date_day)

