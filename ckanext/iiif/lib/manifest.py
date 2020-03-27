import re
from ckan import model
from ckan.plugins import toolkit
from webhelpers.html import HTML

from .utils import create_id_url, create_image_server_url, wrap_language


class IIIFRecordManifestBuilder(object):
    # the group names here must match the parameters for the get_builder function below
    regex = re.compile(u'resource/(?P<resource_id>.*?)/record/(?P<record_id>.*)$')

    @staticmethod
    def get_builder(resource_id, record_id):
        # this will throw an error if the resource can't be found
        resource = toolkit.get_action(u'resource_show')({}, {u'id': resource_id})
        # this will throw an error if the record can't be found
        record = toolkit.get_action(u'record_show')({}, {u'resource_id': resource_id,
                                                         u'record_id': record_id})
        return IIIFRecordManifestBuilder(resource, record[u'data'])

    def __init__(self, resource, record):
        self.resource = resource
        self.record = record
        self.resource_id = resource[u'id']
        self.record_id = record[u'_id']

    @property
    def manifest_id(self):
        return u'resource/{}/record/{}'.format(self.resource_id, self.record_id)

    @property
    def label(self):
        return wrap_language(self.record[self.resource[u'_title_field']])

    @property
    def images(self):
        value = self.record[self.resource[u'_image_field']]
        delimeter = self.resource[u'_image_delimiter']
        return value.split(delimeter) if delimeter else [value]

    @property
    def rights(self):
        # default the license to cc-by
        license_id = self.resource.get(u'_image_licence', u'cc-by')
        license = model.Package.get_license_register()[license_id]
        return HTML.a(license.title, href=license.url)

    @property
    def metadata(self):
        return [
            {u'label': wrap_language(field), u'value': wrap_language(unicode(value))}
            for field, value in self.record.items()
        ]

    def build_canvas(self, image):
        canvas_id = create_id_url(u'{}/canvas/{}'.format(self.manifest_id, image))
        image_id = create_image_server_url(image)

        return {
            u'id': canvas_id,
            u'type': u'Canvas',
            # we don't have access to the image data or metadata here so just use 1000x1000
            u'width': 1000,
            u'height': 1000,
            # TODO: label needs to be using a field defined by the user
            u'label': wrap_language(image),
            u'items': [
                {
                    # TODO: do we need an id here?
                    u'type': u'AnnotationPage',
                    u'items': [
                        {
                            # TODO: do we need an id here?
                            u'type': u'Annotation',
                            u'motivation': u'painting',
                            u'body': {
                                u'id': u'{}/{}'.format(image_id, u'info.json'),
                                u'type': u'Image',
                                u'format': u'image/jpeg',
                                u'service': [
                                    {
                                        u'@context': u'http://iiif.io/api/image/3/context.json',
                                        u'id': image_id,
                                        u'type': u'ImageService3',
                                        u'profile': u'level0'
                                    }
                                ],
                            },
                            u'target': canvas_id,
                        },
                    ]
                }
            ]
        }

    def build(self):
        # TODO: add more properties
        return {
            u'@context': u'http://iiif.io/api/presentation/3/context.json',
            u'id': create_id_url(self.manifest_id),
            u'type': u'Manifest',
            u'label': self.label,
            u'metadata': self.metadata,
            u'rights': self.rights,
            u'items': [self.build_canvas(image) for image in self.images],
        }
