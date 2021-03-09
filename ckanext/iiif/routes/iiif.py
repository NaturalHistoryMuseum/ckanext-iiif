from ckan.plugins import toolkit
from collections import OrderedDict
from flask import Blueprint, jsonify

blueprint = Blueprint(name='iiif', import_name=__name__, url_prefix='/iiif')

builders = OrderedDict()


@blueprint.route('/<path:identifier>')
def resource(identifier):
    for regex, get_builder_function in builders.items():
        match = regex.match(identifier)
        if match:
            builder = get_builder_function(**match.groupdict())
            return jsonify(builder.build())

    return toolkit.abort(status_code=404, detail='Unknown IIIF identifier')
