import ckan.plugins as plugins
import logging
from ckan.plugins import toolkit
from ckantools.loaders import create_actions, create_auth
from contextlib import suppress

from . import interfaces
from . import routes
from .builders.manifest import RecordManifestBuilder
from .logic import actions, auth

log = logging.getLogger(__name__)


class IIIFPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IConfigurable)

    try:
        # hook if we can
        from ckanext.versioned_datastore.interfaces import IVersionedDatastore

        plugins.implements(IVersionedDatastore, inherit=True)
    except ImportError:
        pass

    def get_actions(self):
        """
        IActions hook.
        """
        return create_actions(actions)

    def get_auth_functions(self):
        """
        IAuthFunctions hook.
        """
        return create_auth(auth)

    def configure(self, ckan_config):
        """
        IConfigurable hook. Here, the builders from other plugins are added to the
        BUILDERS list.

        :param ckan_config:
        """
        for plugin in plugins.PluginImplementations(interfaces.IIIIF):
            plugin.register_iiif_builders(actions.BUILDERS)

    def get_blueprint(self):
        """
        IBlueprint hook.
        """
        return routes.blueprints

    def datastore_multisearch_modify_response(self, response):
        """
        IVersionedDatastore hook.

        Only used if ckanext-versioned-datastore is installed.
        """
        resource_cache = {}
        resource_show = toolkit.get_action('resource_show')

        for record in response['records']:
            resource_id = record['resource']
            if resource_id not in resource_cache:
                resource_cache[resource_id] = resource_show({}, {'id': resource_id})
            with suppress(Exception):
                record['iiif'] = RecordManifestBuilder.build_record_manifest(
                    resource_cache[resource_id], record['data']
                )

        return response
