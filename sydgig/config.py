import ConfigParser

config = ConfigParser.ConfigParser()

f = open('config.ini')
config.readfp(f)
f.close()

def get(section, option):
    return config.get(section, option, raw = True)
