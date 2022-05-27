import ckan.plugins as plugins
import logging
from ckan.plugins import toolkit
from contextlib import suppress

from . import interfaces
from . import routes
from .lib.manifest import IIIFRecordManifestBuilder
from .routes import iiif

log = logging.getLogger(__name__)


class IIIFPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(interfaces.IIIIF)

    try:
        # hook if we can
        from ckanext.versioned_datastore.interfaces import IVersionedDatastore
        plugins.implements(IVersionedDatastore, inherit=True)
    except ImportError:
        pass

    # IIIIF
    def get_builders(self):
        return [
            IIIFRecordManifestBuilder,
        ]

    # IConfigurable
    def configure(self, ckan_config):
        for plugin in plugins.PluginImplementations(interfaces.IIIIF):
            for builder in plugin.get_builders():
                if builder.regex in iiif.builders:
                    log.warning('Duplicate IIIF builder regex: {}'.format(builder.regex.pattern))
                iiif.builders[builder.regex] = builder.get_builder

    # IBlueprint
    def get_blueprint(self):
        return routes.blueprints

    # IVersionedDatastore
    def datastore_multisearch_modify_response(self, response):
        resource_cache = {}
        resource_show = toolkit.get_action('resource_show')

        for record in response['records']:
            resource_id = record['resource']
            if resource_id not in resource_cache:
                resource_cache[resource_id] = resource_show({}, {'id': resource_id})
            with suppress(Exception):
                builder = IIIFRecordManifestBuilder(resource_cache[resource_id], record['data'])
                record['iiif'] = builder.build()

        return response
