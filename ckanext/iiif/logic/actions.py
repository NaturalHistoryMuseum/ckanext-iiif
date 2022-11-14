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
    "identifier": [toolkit.get_validator("not_empty"), str],
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
