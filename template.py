from jinja2 import Environment, FileSystemLoader

import urllib, time

def guess_autoescape(template_name):
    if template_name is None or '.' not in template_name:
        return False
    ext = template_name.rsplit('.', 1)[1]
    return ext in ('html', 'htm', 'xml')

def quote_plus(value):
    return urllib.quote_plus(value)

templates = Environment(loader=FileSystemLoader('template/'),
                        autoescape=guess_autoescape,
                        extensions=['jinja2.ext.autoescape'])

templates.filters['quote_plus'] = quote_plus

