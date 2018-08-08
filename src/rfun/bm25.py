import json
from rfun.scoring import ExplanationParser

def parse_solr_results(text):
    j = json.loads(text)
    if 'debug' not in j and 'parsedquery' not in j['debug']:
        raise Exception('No debug output present in the solr response')
    
    query = j['debug']['querystring']
    parsed_query = j['debug']['parsedquery_toString']
    
    explanation = j['debug']['explain']
    
    out = []
    parser = ExplanationParser()
    
    for k,v in explanation.items():
        score, formula = parser.parse(v)
        out.append({'docid': k, 'score': score, 'formula': formula})
        
    return out


def search():     
    pass

if __name__ == '__main__':
    parse_solr_results(open('../../data/or-example.json').read())