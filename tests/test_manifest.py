from ckan import model

from ckanext.iiif.lib.manifest import IIIFRecordManifestBuilder


class TestIIIFRecordManifestBuilder(object):

    def test_manifest_id(self):
        builder = IIIFRecordManifestBuilder({'id': 1}, {'_id': 1})
        assert builder.manifest_id == 'resource/1/record/1'

    def test_label(self):
        builder = IIIFRecordManifestBuilder({'id': 1, '_title_field': 'title'},
                                            {'_id': 1, 'title': 'The title!'})
        assert builder.label == {'en': ['The title!']}

    def test_images_multiple_comma_separated(self):
        builder = IIIFRecordManifestBuilder({'id': 1, '_image_field': 'images',
                                             '_image_delimiter': ','},
                                            {'_id': 1, 'images': 'image1,image2,image3'})
        assert builder.images == ['image1', 'image2', 'image3']

    def test_images_multiple_in_a_list(self):
        builder = IIIFRecordManifestBuilder({'id': 1, '_image_field': 'images'},
                                            {'_id': 1, 'images': ['image1', 'image2', 'image3']})
        assert builder.images == ['image1', 'image2', 'image3']

    def test_images_single_comma_separated(self):
        builder = IIIFRecordManifestBuilder({'id': 1, '_image_field': 'images',
                                             '_image_delimiter': ','},
                                            {'_id': 1, 'images': 'image1'})
        assert builder.images == ['image1']

    def test_images_single(self):
        builder = IIIFRecordManifestBuilder({'id': 1, '_image_field': 'images'},
                                            {'_id': 1, 'images': 'image1'})
        assert builder.images == ['image1']

    def test_rights_default(self):
        builder = IIIFRecordManifestBuilder({'id': 1}, {'_id': 1})
        assert builder.rights == model.Package.get_license_register()['cc-by'].url

    def test_rights_when_set(self):
        builder = IIIFRecordManifestBuilder({'id': 1, '_image_licence': 'cc-zero'}, {'_id': 1})
        assert builder.rights == model.Package.get_license_register()['cc-zero'].url

    def test_metadata(self):
        record_data = {
            'field1': 'beans',
            'field2': 'goats',
        }
        builder = IIIFRecordManifestBuilder({'id': 1}, {u'_id': 1, **record_data})
        metadata = builder.metadata
        assert len(metadata) == 3
        assert {'label': {'en': ['_id']}, 'value': {'en': ['1']}} in metadata
        assert {'label': {'en': ['field1']}, 'value': {'en': ['beans']}} in metadata
        assert {'label': {'en': ['field2']}, 'value': {'en': ['goats']}} in metadata
