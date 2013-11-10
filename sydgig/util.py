import re
import unicodedata
import random
import string

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
def slugify(text, delim=u'-'):
    text = unicode(text)
    result = []
    for word in _punct_re.split(text.lower()):
        word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))

def verify_email(email):
    '''Really dumb email verification. Just checks email is of the form *@*.* without any spaces.'''
    if re.match(r"[^ @]+@[^ @]+\.[^ @]+", email):
        return True
    else:
        return False

def generate_email_verification_code():
    chars = string.letters + string.digits
    return ''.join(random.choice(chars) for i in range(32))