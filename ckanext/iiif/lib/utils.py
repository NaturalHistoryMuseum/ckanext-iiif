from ckan.common import config
from ckan.plugins import toolkit


def create_id_url(identifier):
    return toolkit.url_for(u'iiif.resource', identifier=identifier, _external=True)


def create_image_server_url(image_identifier):
    image_server_url = config.get(u'ckanext.iiif.image_server_url')
    return u'{}/{}'.format(image_server_url, image_identifier)


def wrap_language(value, language=u'en'):
    if not isinstance(value, list):
        value = [value]
    return {language: value}
