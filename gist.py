import json
import re
import requests


class GeneralGist:

    '''
    A general class for GitHub Gists. Is compatible with either the single
    Gist or the multiple Gists JSON API return value.
    '''

    def __init__(self, json):
        self._json = json

    def __getattr__(self, name):
        try:
            return self._json[name]
        except KeyError:
            raise AttributeError

    @property
    def name(self):
        files = self._json.get('files')
        name = files.keys()[0]
        reg = re.compile('(gistfile)(\d+)(.txt)')
        if reg.match(name):
            name = 'gist:%s' % (self.id)
        return name

    @property
    def json(self):
        return json.dumps(self._json, indent=4)

    def __unicode__(self):
        return '<%s "%s">' % (self.__class__.__name__, self.name)

    def __str__(self):
        return self.__unicode__()

class Gist(GeneralGist):

    '''
    A class which implements features that are available in the single
    Gist API return value.
    '''

    def __init__(self, json):
        GeneralGist.__init__(self, json)

    @property
    def filenames(self):
        return self._json.get('files').keys()

    @property
    def files(self):
        return [self.gist_file(filename) for filename in self.filenames]

    def gist_file(self, filename):
        reg = re.compile('^%s$' % filename, re.IGNORECASE)
        for fname in self.filenames:
            match = reg.match(fname)
            if match:
                return GistFile(self._json['files'].get(match.group()))
        raise ValueError('there is no file named "%s"' % filename)


class GistFile:

    '''
    A file within a Gist
    '''

    def __init__(self, json):
        self._json = json

    def __unicode__(self):
        return '<%s "%s">' % (self.__class__.__name__, self.name)

    def __str__(self):
        return self.__unicode__()

    def __getattr__(self, name):
        try:
            return self._json[name]
        except KeyError:
            raise AttributeError

    @property
    def name(self):
        return self._json.get('filename')

class GistAPI:

    def __init__(self, user=None, password=None):
        self.base = 'https://api.github.com'
        if user and password:
            self.user = user
            self.auth = (user, password)
        else:
            self.user = None
            self.auth = None

    def get(self, url):
        if self.auth:
            return requests.get(self.base + url, auth=self.auth)
        else:
            return requests.get(self.base + url)

    def get_gists(self):
        ''' Returns a list of (id, name) tuples for all accessible Gists '''
        r = self.get('/users/%s/gists' % self.user)
        json_gists = r.json()
        gists = map(lambda json: GeneralGist(json), json_gists)
        return [(gist.id, gist.name) for gist in gists]

    def get_gist(self, gist_id):
        ''' Returns a Gist object for the given Gist ID '''
        r = self.get('/gists/%s' % gist_id)
        return Gist(r.json())
