from flask import current_app, request, Blueprint
from flask.ext.discoverer import advertise
from simulateur.models import Experiment
import json
from adsmutils import get_date
from flask.json import jsonify

bp = Blueprint('simulateur', __name__)

@advertise(scopes=[], rate_limit = [100, 3600*24])
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
                        'eid': ex.eid
                        })
        header['remaining'] = max(0, count - (start+rows))
        
        
    return jsonify({'header': header, 'results': out}), 200
    
    
    
    