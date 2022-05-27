from ckan.plugins import toolkit
from typing import Dict


def create_id_url(identifier) -> str:
    return toolkit.url_for('iiif.resource', identifier=identifier, _external=True)


def wrap_language(value, language='en') -> Dict[str, list]:
    if not isinstance(value, list):
        value = [value]
    return {language: value}
