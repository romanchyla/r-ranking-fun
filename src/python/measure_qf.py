
import sys
import os

import config 
from utils import req
from itertools import combinations_with_replacement
import simplejson

log = config.get_logger("rfun.measure_qf")


def run(solr_url, query, haystack,
        qf="title,author", 
        min=0.0, max=2.0, increment=0.25,
        max_hits=100):
    
    min = float(min)
    max = float(max)
    increment = float(increment)
    max_hits = int(max_hits)
    
    if (os.path.exists(query)):
        queries = load_queries(query)
    else:
        queries = [query]
        
    if (os.path.exists(haystack)):
        haystack = load_queries(haystack)
    else:
        haystack = [haystack]    
    
    haystack = [x.split(':', 1) for x in haystack]
    fl = ','.join(list(set([x[0] for x in haystack])))
    combinations = generate_combinations(qf, min, max, increment)
    
    results = {'qf-variations': combinations}
    
    i = 0
    for qf in combinations:
        i = i + 1
        log.info("Starting combination: %s %d/%d" % (qf, i, len(combinations)))
        for q in queries:
            log.info("%s" % q)
            rsp = req(solr_url, q=q, qf=qf, fl=fl, rows=max_hits)
            collect_data(q, qf, results, rsp, haystack)
            
    
    def custom_handler(obj):
        if isinstance(obj, DataPoint):
            return obj.jsonize()
        return obj
    print simplejson.dumps(results, default=custom_handler)       


def generate_combinations(qf, min, max, increment):
    min = float(min)
    max = float(max)
    increment = float(increment)
    
    results = set()
    
    fields = [x.strip() for x in qf.split(",")]
    
    # these codes will serve as increment indicators
    codes = 'ABCDEFGHIJKLMNOPQRSTUVW'[0:len(fields)]
    
    # create raising and falling combinations
    combinations = list(combinations_with_replacement(codes, len(fields)))
    for s in combinations[:]:
        combinations.append(tuple(s))
    combinations = list(set(combinations))
    
    
    # first compute evenly spaced increments in the range min-max
    kw_incr = {}
    inc = (max-min)/len(fields)
    for i in range(1, len(fields)+1):
        kw_incr[chr(64+i)] = i*inc
    
    for c in combinations:
         results.add(' '.join(map(lambda x: '%s^%s' % x, zip(fields, [kw_incr[x] for x in c]))))
         
         
    #next start from the min all the way to the maximum value
    while True:
        l_min = min
        l_max = min + (increment * len(fields))
        l_inc = (l_max - l_min)/len(fields)
        if l_max > max:
            break
        min = min + increment 
        kw_incr.clear()
        
        for i in range(0, len(fields)):
            kw_incr[chr(65+i)] = min+i*l_inc
    
        for c in combinations:
            results.add(' '.join(map(lambda x: '%s^%s' % x, zip(fields, [kw_incr[x] for x in c]))))
            
    return sorted(list(results))
    
    
def collect_data(q, qf, results, rsp, haystack):
    
    if (not results.has_key(q)):
        results[q] = [q]
    row = results[q]
    
    if (not rsp['responseHeader'].has_key('status') or rsp['responseHeader']['status'] != 0):
        log.error("Error searching: %s" % str(rsp))
        row.append(DataPoint(0, 0, [], -1))
        return
    
    qtime = rsp['responseHeader']['QTime']
    numfound = rsp['response']['numFound']
    hits = []
    
    i = 0
    for doc in rsp['response']['docs']:
        i = i + 1
        j = 0
        for field, value in haystack:
            j = j + 1
            value = str(value).lower()
            if (doc.has_key(field)):
                if (isinstance(doc[field], list)):
                    for x in doc[field]:
                        if str(x).lower() == value:
                            hits.append((i, j)) #'%s:%s' % (field, value)
                            break
                else:
                    if doc[field].lower() == value:
                        hits.append((i, j)) #'%s:%s' % (field, value)
                        break
                    
    row.append(DataPoint(qtime, numfound, hits, len(haystack)-len(hits)))
    
     
                

class DataPoint(object):
    def __init__(self, qtime, numfound, hits, misses):
        self.hits = hits
        self.qtime = qtime
        self.numfound = numfound
        self.misses = misses
        
    def __str__(self):
        return '%d/%d' % (self.misses, len(self.hits))
    def __repr__(self):
        return str(self.hits)
    def jsonize(self):
        return {"hits":self.hits, "qtime": self.qtime, "numfound": self.numfound, "misses":self.misses}
        
def load_queries(file):
    fo = open(file, 'r')
    queries = []
    for line in fo:
        if len(line.strip()) > 0 and line[0] != '#':
            queries.append(line.strip())
    return queries

if __name__ == '__main__':
    if 'demo' in sys.argv:
        run("http://adsate:8987/solr/select", "../../data/raw/qf.queries", "../../data/raw/qf.haystack", 
            min=-1, max=1.5, increment=0.5)
        exit(0)
    elif (len(sys.argv) < 3):
        print """usage: python measure_qf.py <solr-url> <file-with-queries|query> <file-with-haystack|query> [qf] [min] [max] [increment] [max_hits] 
        examples:
        python measure_qf.py http://localhost:8984/solr/select queries.txt haystack.txt title,author 0.0 1.5 0.25 100
        """
        exit(0)
    
    
    run(*sys.argv[1:])