import re
import config
from gist import GistAPI

user = config.user
password = config.password


api = GistAPI(user, password)

gists = api.get_gists()

print "Gists:"
for num, info in enumerate(gists):
    id, name = info
    print "%3s: %s" % (num, name)

def get_gist(loc):
    if loc.isdigit():
        id = gists[int(loc)][0]
        return api.get_gist(id)
    else:
        reg = re.compile("^%s$" % loc, re.IGNORECASE)
        for id, name in gists:
            if reg.match(name):
                return api.get_gist(id)
    raise ValueError("No Gist could be found with the locator '%s'" % loc)

print "get gist 0"
mygist = get_gist('0')

def gistfile_header(gistfile):
    s = "%s:" % gistfile.name
    return s

print ''
for gistfile in mygist.files:
    print gistfile_header(gistfile)
    print gistfile.content
    print ''
