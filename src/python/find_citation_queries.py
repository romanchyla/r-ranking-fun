
import sys

import config 
from utils import req
import datetime

log = config.get_logger("rfun.find_citation_queries")

"""
Finds queries that are raising the number of returned 
hits
"""


def run(solr_url,
        query_name='citations',
        fl="title,author,recid,bibcode", 
        min=0, max=2000000, increment=9,
        max_hits=10, max_qtime=60000
        ):
    
    
    results = []
        
    # first start with simple queries
    i = 0
    j = None
    empty = 0
    while True:
        i = i + 1
        j = i + increment
        
        q = "citation_count:[%s TO %s]" % (i,j)
        log.info("%s" % q)
        rsp = req(solr_url, q=q, fl=fl, rows=max_hits, sort="citation_count desc")
        r = select_representative_record(rsp, solr_url, j, query_name)
        if r != None:
            results.append(r)
            empty = 0
        else:
            empty = empty + 1
            
        if empty > 3:
            break
        if j >= max:
            break
        i = j
    
    start_id = max
    end_id = start_id
    incr = 100
    cycle = 1
    while True:
        end_id = end_id + (cycle * (incr * increment))
        q = "id:[%s TO %s]" % (start_id, end_id)
        log.info("%s" % q)
        # first issue the query without citations
        rsp = req(solr_url, q=q, fl=fl, rows=1)
        # now execute the functional query
        rsp = req(solr_url, q=("%s(%s)" % (query_name, q)), fl=fl, rows=1)
        if (not rsp['responseHeader'].has_key('status') or rsp['responseHeader']['status'] != 0):
            log.error("Error searching: %s" % str(rsp))
            continue
        numfound = rsp['response']['numFound']
        qtime = rsp['responseHeader']['QTime']
        results.append((q, numfound, qtime))
        if numfound > max or qtime > max_qtime:
            log.info("Stopping because qtime too high: %s" % (qtime,))
            break
        log.info("last found: q=%s, num=%s, qtime=%s" % (q, numfound, qtime))
        cycle += 1
        
    today = datetime.date.today()
    previous = today
    resolution = 30
    stop_day = datetime.date.fromordinal(today.toordinal()-(365*2))
    
    while False:
        q = "pubdate:[%s TO %s]" % (str(previous),str(today))
        log.info("%s" % q)
        # now execute the functional query
        rsp = req(solr_url, q=("%s(%s)" % (query_name, q)), fl=fl, rows=1)
        if (not rsp['responseHeader'].has_key('status') or rsp['responseHeader']['status'] != 0):
            log.error("Error searching: %s" % str(rsp))
            continue
        numfound = rsp['response']['numFound']
        qtime = rsp['responseHeader']['QTime']
        results.append((q, numfound, qtime))
        previous = previous.fromordinal(previous.toordinal() - resolution)
        
        if previous < stop_day:
            break
    
    print "#%s" % (query_name,)
    print "query\tnumFound\tQTime"
    print "\n".join(map(lambda x: "%s\t%s\t%s" % x, results))       


def select_representative_record(rsp, solr_url, j, query_name):
    if not rsp['response'].has_key('docs'):
        return None
    
    tmp_results = []
    for doc in rsp['response']['docs']:
        q = "bibcode:%s" % doc['bibcode']
        cit_rsp = req(solr_url, q=("%s(%s)" % (query_name, q)), fl="citation_count", rows=0)
        
        if (not cit_rsp['responseHeader'].has_key('status') or cit_rsp['responseHeader']['status'] != 0):
            log.error("Error searching: %s" % str(rsp))
            continue
        numfound = cit_rsp['response']['numFound']
        qtime = cit_rsp['responseHeader']['QTime']
        tmp_results.append((q, numfound, qtime))
        if numfound == j:
            break
    
    if len(tmp_results):
        return sorted(tmp_results, key=lambda x: abs((x[1] % j)))[0]
    
    

        
def load_queries(file):
    fo = open(file, 'r')
    queries = []
    for line in fo:
        if len(line.strip()) > 0 and line[0] != '#':
            queries.append(line.strip())
    return queries

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print """usage: python measure_qf.py <solr-url> <file-with-queries|query> [qf] [min] [max] [increment] 
        examples:
        python measure_qf.py http://localhost:8984/solr/select queries.txt 10 title,author 0.0 1.5 0.25
        """
        exit(0)
    
    run(*sys.argv[1:])