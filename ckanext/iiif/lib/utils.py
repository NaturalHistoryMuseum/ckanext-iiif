from ckan.common import config
from ckan.plugins import toolkit


def create_id_url(identifier):
    return toolkit.url_for('iiif.resource', identifier=identifier, _external=True)


def wrap_language(value, language='en'):
    if not isinstance(value, list):
        value = [value]
    return {language: value}
