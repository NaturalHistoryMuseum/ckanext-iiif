from ckan.plugins import interfaces
from typing import Optional, Callable, OrderedDict


class IIIIF(interfaces.Interface):
    """
    This (horribly named) interface allows other plugins to hook into the IIIF plugin.
    """

    def register_iiif_builders(
        self, builders: OrderedDict[str, Callable[[str], Optional[dict]]]
    ):
        """
        Hook for registering IIIF builders.
        """
        pass
