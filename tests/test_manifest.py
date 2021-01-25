from ckan import model
from mock import MagicMock

from ckanext.iiif.lib.manifest import IIIFRecordManifestBuilder


class TestIIIFRecordManifestBuilder(object):

    def test_manifest_id(self):
        builder = IIIFRecordManifestBuilder({u'id': 1}, {u'_id': 1})
        assert builder.manifest_id == u'resource/1/record/1'

    def test_label(self):
        builder = IIIFRecordManifestBuilder({u'id': 1, u'_title_field': u'title'},
                                            {u'_id': 1, u'title': u'The title!'})
        assert builder.label == {u'en': [u'The title!']}

    def test_images_multiple_comma_separated(self):
        builder = IIIFRecordManifestBuilder({u'id': 1, u'_image_field': u'images',
                                             u'_image_delimiter': u','},
                                            {u'_id': 1, u'images': u'image1,image2,image3'})
        assert builder.images == [u'image1', u'image2', u'image3']

    def test_images_multiple_in_a_list(self):
        builder = IIIFRecordManifestBuilder({u'id': 1, u'_image_field': u'images'},
                                            {u'_id': 1,
                                             u'images': [u'image1', u'image2', u'image3']})
        assert builder.images == [u'image1', u'image2', u'image3']

    def test_images_single_comma_separated(self):
        builder = IIIFRecordManifestBuilder({u'id': 1, u'_image_field': u'images',
                                             u'_image_delimiter': u','},
                                            {u'_id': 1, u'images': u'image1'})
        assert builder.images == [u'image1']

    def test_images_single(self):
        builder = IIIFRecordManifestBuilder({u'id': 1, u'_image_field': u'images'},
                                            {u'_id': 1, u'images': u'image1'})
        assert builder.images == [u'image1']

    def test_rights_default(self):
        builder = IIIFRecordManifestBuilder({u'id': 1}, {u'_id': 1})
        assert builder.rights == model.Package.get_license_register()[u'cc-by'].url

    def test_rights_when_set(self):
        builder = IIIFRecordManifestBuilder({u'id': 1, u'_image_licence': u'cc-zero'}, {u'_id': 1})
        assert builder.rights == model.Package.get_license_register()[u'cc-zero'].url

    def test_metadata(self):
        record_data = {
            u'field1': u'beans',
            u'field2': u'goats',
        }
        builder = IIIFRecordManifestBuilder({u'id': 1}, dict(_id=1, **record_data))
        metadata = builder.metadata
        assert len(metadata) == 3
        assert {u'label': {u'en': [u'_id']}, u'value': {u'en': [u'1']}} in metadata
        assert {u'label': {u'en': [u'field1']}, u'value': {u'en': [u'beans']}} in metadata
        assert {u'label': {u'en': [u'field2']}, u'value': {u'en': [u'goats']}} in metadata
