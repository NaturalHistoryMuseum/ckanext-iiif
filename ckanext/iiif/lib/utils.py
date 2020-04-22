from ckan.common import config
from ckan.plugins import toolkit


def create_id_url(identifier):
    return toolkit.url_for(u'iiif.resource', identifier=identifier, _external=True)


def create_image_server_url(identifier_name, identifier_type=u'vfactor'):
    image_server_url = config.get(u'ckanext.iiif.image_server_url')
    return u'{}/{}:{}'.format(image_server_url, identifier_type, identifier_name)


def wrap_language(value, language=u'en'):
    if not isinstance(value, list):
        value = [value]
    return {language: value}
