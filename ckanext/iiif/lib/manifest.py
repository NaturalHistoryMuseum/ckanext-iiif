import re
from ckan import model
from ckan.common import config
from ckan.plugins import toolkit
from typing import List

from .utils import create_id_url, wrap_language


class IIIFRecordManifestBuilder:
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
    def images(self) -> List[str]:
        value = self.record[self.resource['_image_field']]
        image_delimiter = self.resource.get('_image_delimiter', None)
        if image_delimiter:
            return value.split(image_delimiter)
        else:
            images = value if isinstance(value, list) else [value]
            if isinstance(images[0], dict):
                return [image['identifier'] for image in images]
            else:
                return images

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

    def build_canvas(self, image_number: int, image_id: str) -> dict:
        canvas_id = create_id_url(f'{self.manifest_id}/canvas/{image_number}')

        return {
            'id': canvas_id,
            'type': 'Canvas',
            # we don't have access to the image data or metadata here so just use 1000x1000
            'width': 1000,
            'height': 1000,
            # TODO: label needs to be using a field defined by the user
            'label': wrap_language(image_id),
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
            'items': [self.build_canvas(i, image) for i, image in enumerate(self.images)],
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
