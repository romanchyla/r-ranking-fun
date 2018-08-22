from flask import current_app, request, Blueprint
from flask.ext.discoverer import advertise

bp = Blueprint('simulateur', __name__)

@advertise(scopes=[], rate_limit = [100, 3600*24])
@bp.route('/foo', methods=['GET'])
def foo():
    pass