import re
from ckan import model
from ckan.common import config
from ckan.lib.helpers import url_for_static_or_external
from ckan.logic import NotFound
from ckan.plugins import toolkit
from typing import List, Dict, Optional, Union

from .abc import IIIFResourceBuilder
from .utils import create_id_url, wrap_language, IIIFBuildError


class RecordManifestBuilder(IIIFResourceBuilder):
    BUILDER_ID = 'record'

    def build_identifier(self, resource_id: str, record_id: Union[str, int]) -> str:
        """
        Given a resource_id and a record_id, builds the record manifest identifier and
        returns it.

        :param resource_id: the resource ID
        :param record_id: the record ID
        :return: the identifier
        """
        return RecordManifestBuilder._build_record_manifest_id(
            resource_id, str(record_id)
        )

    def match_and_build(self, identifier: str) -> Optional[dict]:
        """
        Build the manifest for the given resource id & record id identifier. If the
        identifier does not match format required then None is returned, otherwise an
        attempt to build the manifest is made and any issues will result in raised
        exceptions.

        :param identifier: the manifest ID
        :return: the manifest as a dict or None if the identifier wasn't a match to the
                 required format
        :raise: IIIFBuildError if anything goes wrong after the identifier is matched
        """
        regex = re.compile('resource/(?P<resource_id>.+?)/record/(?P<record_id>.+)$')
        match = regex.match(identifier)
        if not match:
            return None
        resource_id, record_id = match.groups()

        try:
            resource = toolkit.get_action('resource_show')({}, {'id': resource_id})
        except NotFound:
            raise IIIFBuildError(identifier, f'Resource {resource_id} not found')

        try:
            result = toolkit.get_action('record_show')(
                {}, {'resource_id': resource_id, 'record_id': record_id}
            )
            # we're only going to use the data part
            record = result['data']
        except NotFound:
            raise IIIFBuildError(identifier, f'Record {record_id} not found')

        return RecordManifestBuilder.build_record_manifest(resource, record)

    @staticmethod
    def build_record_manifest(resource: dict, record: dict) -> Optional[dict]:
        """
        Given a resource and a record, build a IIIF manifest for the images held within
        the record.

        :param resource: the resource dict
        :param record: the record data
        :return: the IIIF manifest for the record and its images
        :raise: IIIFBuildError if no images are present on the record
        """
        manifest_id = RecordManifestBuilder._build_record_manifest_id(resource, record)

        images = RecordManifestBuilder._get_images(resource, record)
        # if there are no images, raise an exception
        if not images:
            raise IIIFBuildError(manifest_id, 'No images found')

        # TODO: add more properties
        return {
            '@context': 'http://iiif.io/api/presentation/3/context.json',
            'id': create_id_url(manifest_id),
            'type': 'Manifest',
            'label': RecordManifestBuilder._build_label(resource, record),
            'metadata': RecordManifestBuilder._build_metadata(record),
            'rights': RecordManifestBuilder._build_rights(resource),
            'items': [
                RecordManifestBuilder._build_canvas(manifest_id, i, image)
                for i, image in enumerate(images)
            ],
            'logo': [
                {
                    'id': url_for_static_or_external(config.get('ckan.site_logo')),
                    'type': 'Image',
                    # TODO: need get these from somewhere dynamic?
                    'format': 'image/png',
                    'width': 120,
                    'height': 56,
                }
            ],
        }

    @staticmethod
    def _build_record_manifest_id(
        resource: Union[dict, str], record: Union[dict, str, int]
    ) -> str:
        """
        Builds the manifest ID from the given resource and record dicts or IDs. If this
        ID is given to the build_iiif_resource action then the manifest for this
        resource and record combination should be returned.

        :param resource: the resource dict or resource ID
        :param record: the record dict or record ID
        :return: the manifest ID
        """
        resource_id = resource['id'] if isinstance(resource, dict) else resource
        record_id = record['_id'] if isinstance(record, dict) else record
        return f'resource/{resource_id}/record/{record_id}'

    @staticmethod
    def _build_label(resource: dict, record: dict) -> Dict[str, List[str]]:
        """
        Returns the label to use for the given resource and record. Currently, this uses
        the 'title field' if specified on the resource. If the 'title field' isn't
        available then the record ID is used.

        :param resource: the resource dict
        :param record: the record dict
        :return: the label to use for this manifest
        """
        title_field = resource.get('_title_field')
        if not title_field:
            title_field = '_id'
        # make sure the value is a string (this should only be necessary if the _id is
        # used)
        return wrap_language(str(record[title_field]))

    @staticmethod
    def _build_rights(resource: dict) -> str:
        """
        Returns the rights to use in the given resource's manifest. If no license is
        specified on the resource then cc-by is used as a default.

        :param resource: the resource dict
        :return: the license URL to use
        """
        license_id = resource.get('_image_licence', None)
        # if the license is '' or None we override it
        if not license_id:
            # default the license to cc-by
            license_id = 'cc-by'
        return model.Package.get_license_register()[license_id].url

    @staticmethod
    def _build_metadata(record: dict) -> List[Dict[str, Dict[str, list]]]:
        """
        Given a record dict, builds a list of language wrapped values to use in the
        manifest. This loops through every field in the record and adds it to the
        returned list.

        :param record: the record dict
        :return: a list of language wrapped labels and values
        """
        # TODO: handle nested dicts and lists
        metadata = []
        for field, value in record.items():
            if isinstance(value, list):
                value = list(map(str, value))
            elif not isinstance(value, str):
                value = str(value)
            metadata.append(
                {'label': wrap_language(field), 'value': wrap_language(value)}
            )

        return metadata

    @staticmethod
    def _build_canvas(manifest_id: str, image_number: int, image_id: str) -> dict:
        """
        Builds a canvas dict for the given image.

        :param manifest_id: the manifest id
        :param image_number: the image number on the record
        :param image_id: the image URL
        :return: the canvas definition
        """
        canvas_id = create_id_url(f'{manifest_id}/canvas/{image_number}')
        annotation_page_id = f'{canvas_id}/0'
        annotation_id = f'{annotation_page_id}/0'

        return {
            'id': canvas_id,
            'type': 'Canvas',
            # we don't have access to the image data or metadata here so just use
            # 1000x1000
            'width': 1000,
            'height': 1000,
            # TODO: label needs to be using a field defined by the user
            'label': wrap_language(image_id),
            'items': [
                {
                    'id': annotation_page_id,
                    'type': 'AnnotationPage',
                    'items': [
                        {
                            'id': annotation_id,
                            'type': 'Annotation',
                            'motivation': 'painting',
                            'body': {
                                'id': image_id,
                                'type': 'Image',
                            },
                            'target': canvas_id,
                        },
                    ],
                }
            ],
        }

    @staticmethod
    def _get_images(resource: dict, record: dict) -> List[str]:
        """
        Given a resource (for the image settings) and the record data, return any images
        found within as a list of URLs.

        :param resource: the resource dict
        :param record: the record data dict
        :return: a list of image URLs
        """
        image_field = resource.get('_image_field')
        if not image_field or image_field not in record:
            return []

        value = record[image_field]

        if isinstance(value, list):
            # TODO: handle mix of dicts and str?
            # TODO: handle non-'identifier' keyed urls?
            if isinstance(value[0], dict):
                return [image['identifier'] for image in value]
            else:
                return value
        else:
            image_delimiter = resource.get('_image_delimiter')
            return value.split(image_delimiter) if image_delimiter else [value]
