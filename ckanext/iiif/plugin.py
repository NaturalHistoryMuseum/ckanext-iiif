import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from . import interfaces
from . import routes
from .routes import iiif
from .lib.manifest import IIIFRecordManifestBuilder


class IIIFPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(interfaces.IIIIF)

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
                    continue
                    # TODO: this
                    # raise Exception(u'Duplicate IIIF builder regex: {}'.format(regex.pattern))
                iiif.builders[builder.regex] = builder.get_builder

    # IBlueprint
    def get_blueprint(self):
        return routes.blueprints
