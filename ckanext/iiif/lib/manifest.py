import re
from ckan import model
from ckan.common import config
from ckan.plugins import toolkit

from .utils import create_id_url, create_image_server_url, wrap_language


class IIIFRecordManifestBuilder(object):
    # the group names here must match the parameters for the get_builder function below
    regex = re.compile('resource/(?P<resource_id>.+?)/record/(?P<record_id>.+)$')

    @staticmethod
    def get_builder(resource_id, record_id):
        # this will throw an error if the resource can't be found
        resource = toolkit.get_action('resource_show')({}, {'id': resource_id})
        # this will throw an error if the record can't be found
        record = toolkit.get_action('record_show')({}, {'resource_id': resource_id,
                                                        'record_id': record_id})
        return IIIFRecordManifestBuilder(resource, record['data'])

    def __init__(self, resource, record):
        self.resource = resource
        self.record = record
        self.resource_id = resource['id']
        self.record_id = record['_id']

    @property
    def manifest_id(self):
        return f'resource/{self.resource_id}/record/{self.record_id}'

    @property
    def label(self):
        return wrap_language(self.record[self.resource['_title_field']])

    @property
    def images(self):
        value = self.record[self.resource['_image_field']]
        image_delimiter = self.resource.get('_image_delimiter', None)
        if image_delimiter:
            return value.split(image_delimiter)
        else:
            return value if isinstance(value, list) else [value]

    @property
    def rights(self):
        license_id = self.resource.get('_image_licence', None)
        # if the license is '' or None we override it
        if not license_id:
            # default the license to cc-by
            license_id = 'cc-by'
        license = model.Package.get_license_register()[license_id]
        return license.url

    @property
    def metadata(self):
        # TODO: this function does not handle lists of values well, nor nested dicts...
        return [
            {'label': wrap_language(field), 'value': wrap_language(str(value))}
            for field, value in self.record.items()
        ]

    def build_canvas(self, image):
        canvas_id = create_id_url(f'{self.manifest_id}/canvas/{image}')
        # TODO: need to pass the type based on some logic (user setting/custom code)
        image_id = create_image_server_url(image)

        return {
            'id': canvas_id,
            'type': 'Canvas',
            # we don't have access to the image data or metadata here so just use 1000x1000
            'width': 1000,
            'height': 1000,
            # TODO: label needs to be using a field defined by the user
            'label': wrap_language(image),
            'items': [
                {
                    # TODO: do we need an id here?
                    'type': 'AnnotationPage',
                    'items': [
                        {
                            # TODO: do we need an id here?
                            'type': 'Annotation',
                            'motivation': 'painting',
                            'body': {
                                'id': f'{image_id}/info.json',
                                'type': 'Image',
                                'format': 'image/jpeg',
                                'service': [
                                    {
                                        '@context': 'http://iiif.io/api/image/3/context.json',
                                        'id': image_id,
                                        'type': 'ImageService3',
                                        'profile': 'level0'
                                    }
                                ],
                            },
                            'target': canvas_id,
                        },
                    ]
                }
            ]
        }

    def build(self):
        # TODO: add more properties
        return {
            '@context': 'http://iiif.io/api/presentation/3/context.json',
            'id': create_id_url(self.manifest_id),
            'type': 'Manifest',
            'label': self.label,
            'metadata': self.metadata,
            'rights': self.rights,
            'items': [self.build_canvas(image) for image in self.images],
            'logo': [
                {
                    'id': f'{config.get("ckan.site_url")}/images/logo.png',
                    'type': 'Image',
                    'format': 'image/png',
                    'width': 120,
                    'height': 56,
                }
            ],
        }
