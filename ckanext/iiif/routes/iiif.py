from ckan.plugins import toolkit
from flask import Blueprint, jsonify

blueprint = Blueprint(name='iiif', import_name=__name__, url_prefix='/iiif')


@blueprint.route('/<path:identifier>')
def resource(identifier):
    result = toolkit.get_action('build_iiif_resource')({}, {'identifier': identifier})
    if result:
        return jsonify(result)
    else:
        return toolkit.abort(status_code=404, detail='Unknown IIIF identifier')
