from flask import current_app, request, Blueprint
from flask.ext.discoverer import advertise
from simulateur.models import Experiment
import json
from adsmutils import get_date
from flask.json import jsonify
import urlparse

bp = Blueprint('simulateur', __name__)


@advertise(scopes=[], rate_limit = [5000, 3600*24])
@bp.route('/experiment/<experimentid>', methods=['GET', 'POST'])
def experiment(experimentid):
    
    if experimentid == '-1': # create a new one
        exp = current_app.save_experiment(None)
    else:
        exp = current_app.get_experiment(experimentid)
        if exp is None:
            return jsonify({'error': 'No experiment with such id: %s exists' % experimentid}), 404
    
    if request.method == 'GET':
        return jsonify(exp), 200
    else:
        payload = get_payload(request)
        
        verb = payload.get('verb', 'none')
        data = payload.get('data', [])
        out = {}
        
        if verb == 'add-relevant':
            k = set(data)
            for r in k.difference(set(exp['relevant'])):
                exp['relevant'].append(r)
            out = current_app.save_experiment(exp['eid'], relevant=exp['relevant'])
        elif verb == 'remove-relevant':
            k = set(data)
            for r in k.intersection(set(exp['relevant'])):
                exp['relevant'].remove(r)
            out = current_app.save_experiment(exp['eid'], relevant=exp['relevant'])
        elif verb == 'replace-relevant':
            exp['relevant'] = data
            out = current_app.save_experiment(exp['eid'], relevant=exp['relevant'])
        elif verb == 'save-experiment':
            kwargs = {'experiment_params': _extract_experiment_params(data)}
            if 'reporter' in data:
                kwargs['reporter'] = data['reporter']
            out = current_app.save_experiment(exp['eid'], **kwargs)
        elif verb == 'update-experiment':
            d = exp['experiment_params']
            d.update(_extract_experiment_params(data))
            kwargs = {}
            kwargs['experiment_params'] = d
            if 'reporter' in data:
                kwargs['reporter'] = data['reporter']
            out = current_app.save_experiment(exp['eid'], **kwargs)
        else:
            return jsonify({'error': 'unknown action: %s' % verb}), 404
            
        
        return jsonify(out), 200
            


@advertise(scopes=[], rate_limit = [1000, 3600*24])
@bp.route('/search/<experimentid>', methods=['GET'])
def search(experimentid):
    args=dict(request.args)
    
    # search api, get data
    results = current_app.enhance_solr_results(current_app.search(**args))
    
    # save results into the db
    current_app.save_experiment(experimentid, query_results=results)
    return jsonify(results), 200
    
    
    
@advertise(scopes=[], rate_limit = [100, 3600*24])
@bp.route('/dashboard', methods=['GET'])
@bp.route('/dashboard/<start>/<rows>', methods=['GET'])
def dashboard(start=0, rows=50):
    """Paginates through the list of (existing) experiments"""
    out = []
    start = int(start)
    rows = int(rows)
    
    header = {'start': start, 'rows': rows}
    with current_app.session_scope() as session:
        count = int(session.query(Experiment).count())
        
        # todo(rca): is there a better way?
        if start:
            last_eid = 0
            for ex in session.query(Experiment).order_by(Experiment.eid.asc()).limit(start).all():
                last_eid = ex.eid
            start = last_eid
        
        for ex in session.query(Experiment).order_by(Experiment.eid.asc())\
            .filter(Experiment.eid >= start).limit(rows).all():
            out.append({'query': ex.query, 'reporter': ex.reporter, 
                        'created': get_date(ex.created).isoformat(),
                        'eid': ex.eid, 'info': _get_exp_info(ex.toJSON())
                        })
        header['remaining'] = max(0, count - (start+rows))
        
        
    return jsonify({'header': header, 'results': out}), 200

def _get_exp_info(exp):
    num_found = num_used = num_golden = 0    
    if exp['query_results']:
        if 'response' in exp['query_results']:
            num_found = exp['query_results']['response']['numFound']
        num_used = len(exp['query_results']['response']['docs'])
        num_golden = len(exp['relevant'])
    return '%s/%s/%s' % (num_found, num_used, num_golden)
    
    

def get_payload(request):
    headers = dict(request.headers)
    if 'Content-Type' in headers \
        and 'application/json' in headers['Content-Type'] \
        and request.method in ('POST', 'PUT'):
        payload = request.json
    else:
        payload = dict(request.args)
        payload.update(dict(request.form))
    
    return payload


    
def _extract_experiment_params(data):
    out = {}
    for x in ('kRange:floatrange', 'bRange:floatrange', 'docLenRange:floatrange', 
              'fieldBoost:str', 'normalizeWeight:bool', 'qparams:dict', 'extra_params:urlparams'):
        k,t = x.split(':')
        if k in data:
            if t == 'floatrange':
                x = data[k]
                out[k] = (float(x[0]), float(x[1]))
            elif t == 'float':
                out[k] = float(data[k])
            elif t == 'bool':
                x = str(data[k]).lower()
                if x == 'true' or x == '1':
                    out[k] = True
                else:
                    out[k] = False
            elif t == 'str':
                out[k] = str(data[k])
            elif t == 'dict':
                if not isinstance(data[k], dict):
                    raise Exception('Incompatible type, expecting: %s, got: %s' % (t, data[k]))
                out[k] = data[k]
            elif t == 'urlparams':
                if isinstance(data[k], dict):
                    out[k] = data[k]
                else:
                    out[k] = urlparse.parse_qs(data[k])
            else:
                raise Exception('shouldnt happen, unknown type: %s' % t)
    if 'query' in out:
        out.setdefault('extra_params', {})
        out['extra_params']['q'] = out['query']
    return out
        
        
        
    