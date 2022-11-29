from typing import Optional

import abc


class IIIFResourceBuilder(abc.ABC):
    """
    Abstract base class for a IIIF resource builder.

    Subclasses should be registered with the IIIF plugin as builders using the
    register_iiif_builders function on the IIIIF interface.
    """

    @abc.abstractmethod
    def match_and_build(self, identifier: str) -> Optional[dict]:
        ...

    @abc.abstractmethod
    def build_identifier(self, **kwargs) -> str:
        # this is called from an action so only kwargs are used
        ...
