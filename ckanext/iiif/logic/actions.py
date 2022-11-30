from collections import OrderedDict

import logging
from ckan.plugins import toolkit
from ckantools.decorators import action
from typing import Optional, OrderedDict as OrderedDictType

from ..builders.abc import IIIFResourceBuilder
from ..builders.manifest import RecordManifestBuilder
from ..builders.utils import IIIFBuildError

log = logging.getLogger(__name__)

BUILDERS: OrderedDictType[str, IIIFResourceBuilder] = OrderedDict()

# register the basic record manifest builder by default
BUILDERS[RecordManifestBuilder.BUILDER_ID] = RecordManifestBuilder()

build_iiif_resource_schema = {
    'identifier': [toolkit.get_validator('not_empty'), str],
}
build_iiif_resource_help = """
Given an identifier, builds the corresponding IIIF resource (e.g. manifest) and returns
it as a dict (or JSON if calling action via HTTP).

Params:
- identifier: the IIIF resource identifier as a string

Returns: a dict or None if no builder could be found to build the identifier
"""


@action(build_iiif_resource_schema, build_iiif_resource_help, toolkit.side_effect_free)
def build_iiif_resource(identifier: str) -> Optional[dict]:
    """
    Given a IIIF resource identifier, build the resource from the first matching builder
    in the BUILDERS list and then return the result. If no builder can be matched then
    None is returned.

    :param identifier: the IIIF resource identifier
    :return: a dict or None
    """
    for builder in BUILDERS.values():
        try:
            result = builder.match_and_build(identifier)
            if result is not None:
                return result
        except IIIFBuildError as e:
            log.error(str(e), exc_info=e)
            break
    return None


build_iiif_identifier_schema = {
    'builder_id': [toolkit.get_validator('not_empty'), str],
}
build_iiif_identifier_help = """
Given a builder ID plus args and kwargs, builds the corresponding IIIF resource
identifier and returns it as a string.

Params:
- identifier: the IIIF resource identifier as a string
- args: list of other arguments to build the ID with
- kwargs: dict of keyword arguments to build the ID with

Returns: a str or None if no builder could be found to build the identifier
"""


@action(
    build_iiif_identifier_schema, build_iiif_identifier_help, toolkit.side_effect_free
)
def build_iiif_identifier(builder_id: str, original_data_dict: dict) -> Optional[str]:
    if builder_id not in BUILDERS:
        return None

    if not original_data_dict:
        original_data_dict = {}
    else:
        original_data_dict.pop('builder_id', None)
    return BUILDERS[builder_id].build_identifier(**original_data_dict)
