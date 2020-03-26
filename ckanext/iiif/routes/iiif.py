from collections import OrderedDict

from ckan.plugins import toolkit
from flask import Blueprint, jsonify

blueprint = Blueprint(name=u'iiif', import_name=__name__, url_prefix=u'/iiif')

builders = OrderedDict()


@blueprint.route(u'/<path:identifier>')
def resource(identifier):
    for regex, get_builder_function in builders.items():
        match = regex.match(identifier)
        if match:
            builder = get_builder_function(**match.groupdict())
            return jsonify(builder.build())

    return toolkit.abort(status_code=404, detail=u'Unknown IIIF identifier')
