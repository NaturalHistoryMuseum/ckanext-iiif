from ckan.plugins import toolkit
from typing import Dict, List, Union


def create_id_url(identifier: str) -> str:
    """
    Given the identifier of a IIIF resource, creates the full URL for it.

    :param identifier: the IIIF resource ID
    :return: the full URL for the IIIF resource (e.g. a manifest)
    """
    return toolkit.url_for('iiif.resource', identifier=identifier, _external=True)


def wrap_language(value: Union[str, List[str]], language='en') -> Dict[str, List[str]]:
    """
    Wraps the given value in the appropriate structure required by IIIF to convey language options.

    :param value: the value/values
    :param language: the language, defaults to "en"
    :return: the value in the right IIIF language format
    """
    if not isinstance(value, list):
        value = [value]
    return {language: value}
