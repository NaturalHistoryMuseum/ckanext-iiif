from ckan.plugins import interfaces
from typing import Optional, Callable, List


class IIIIF(interfaces.Interface):
    """
    This (horribly named) interface allows other plugins to hook into the IIIF plugin.
    """

    def register_iiif_builders(self, builders: List[Callable[[str], Optional[dict]]]):
        """
        Hook for registering IIIF builders.
        """
        pass
