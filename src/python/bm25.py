import json


def parse_solr_debug_output(text):
    j = json.loads(text)
    if 'debug' not in j and 'parsedquery' not in j['debug']:
        raise Exception('No debug output present in the solr response')
    
    query = j['debug']['querystring']
    parsed_query = j['debug']['parsedquery_toString']
    
    explanation = j['debug']['explain']
    
    out = []
    for k,v in explanation.items():
        print v
        print "\n----------------------------\n"
        vals = parse_score_explanation(v)
        vals['id'] = k
        out.append(vals)
        
    print json.dumps(out, indent=True)
    
def parse_score_explanation(text, out=None):
    if out is None:
        out = {}
    # general strcuture is value = explanation
    def map_key(k, v, out):
        if 'weight' in k:
            weight = k.split('[SchemaSimilarity]')[0].strip()
            if 'terms' not in out:
                out['terms'] = []
            qterm = weight.rsplit(' ', 2)[0][7:]
            out['terms'].append(qterm)
            return 'weight'
        elif 'score(' in k:
            return 'score'
        elif 'idf()' in k:
            # nested structure
            out['idf()'] = {}
            parse_score_explanation(v, out['idf()'])
        elif 'idf(' in k:
            print k
            docfreq,doccount = k.strip()[4:-1].split(', ')
            docfreq=int(docfreq.split('=')[1])
            doccount=int(doccount.split('=')[1])
            out['docFreq'] = int(docfreq)
            out['docCount'] = int(doccount)
            return 'idf'
        elif 'tfNorm' in k:
            return 'tfNorm'
        elif 'parameter k1' in k:
            return 'k1'
        elif 'parameter b' in k:
            return 'b'
        else:
            return k.strip()
    
    x = text.split('\n')
    for x in reversed(x):
        if ' = ' not in x:
            continue
        v,k = x.split(' = ', 1)
        new_key = map_key(k, v, out)
        if new_key:
            out[new_key] = float(v.strip())
    return out
            
if __name__ == '__main__':
    parse_solr_debug_output(open('../../data/or-example.json').read())