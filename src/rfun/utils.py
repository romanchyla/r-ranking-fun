
import simplejson
import urllib
import copy
import json



def req(url, **kwargs):
    kwargs['wt'] = 'json'
    params = urllib.urlencode(kwargs)
    page = ''
    conn = urllib.urlopen(url, params)
    page = conn.read()
    rsp = simplejson.loads(page)
    conn.close()
    return rsp



if __name__ == '__main__':
    parse_solr_results(open('../../data/or-example.json').read())