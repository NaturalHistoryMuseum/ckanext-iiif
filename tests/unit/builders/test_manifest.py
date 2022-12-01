import pytest
from ckan.logic import NotFound
from ckan.plugins import toolkit
from ckan.tests import factories
from unittest.mock import patch, MagicMock

from ckanext.iiif.builders.manifest import RecordManifestBuilder
from ckanext.iiif.builders.utils import wrap_language, IIIFBuildError


class TestBuildManifestID:
    def test_dicts(self):
        manifest_id = RecordManifestBuilder._build_record_manifest_id(
            {'id': '5'}, {'_id': '829'}
        )
        assert manifest_id == 'resource/5/record/829'

    def test_str_ids(self):
        manifest_id = RecordManifestBuilder._build_record_manifest_id('5', '829')
        assert manifest_id == 'resource/5/record/829'

    def test_int_record_id(self):
        manifest_id = RecordManifestBuilder._build_record_manifest_id('5', 829)
        assert manifest_id == 'resource/5/record/829'


class TestBuildLabel:
    def test_with_title_field(self):
        title_field = 'fieldX'
        title_value = 'The title!'
        label = RecordManifestBuilder._build_label(
            {'_title_field': title_field}, {title_field: title_value}
        )
        assert label == wrap_language(title_value)

    def test_without_title_field(self):
        record_id = 52
        label = RecordManifestBuilder._build_label({}, {'_id': record_id})
        assert label == wrap_language(str(record_id))

    @pytest.mark.parametrize('title_field', [None, ''])
    def test_with_blank_title_field(self, title_field: str):
        record_id = 52
        label = RecordManifestBuilder._build_label(
            {'_title_field': title_field}, {'_id': record_id, title_field: 'lol no'}
        )
        assert label == wrap_language(str(record_id))


class TestBuildRights:
    def test_with_image_licence(self):
        licence_url = RecordManifestBuilder._build_rights({'_image_licence': 'cc-zero'})
        assert licence_url == 'http://www.opendefinition.org/licenses/cc-zero'

    def test_without_image_licence(self):
        licence_url = RecordManifestBuilder._build_rights({})
        assert licence_url == 'http://www.opendefinition.org/licenses/cc-by'


class TestBuildMetadata:
    def test_int(self):
        record = {
            'int': 40,
        }
        metadata = RecordManifestBuilder._build_metadata(record)
        assert len(metadata) == 1
        assert metadata[0] == {
            'label': wrap_language('int'),
            'value': wrap_language('40'),
        }

    def test_str(self):
        record = {
            'str': 'beans',
        }
        metadata = RecordManifestBuilder._build_metadata(record)
        assert len(metadata) == 1
        assert metadata[0] == {
            'label': wrap_language('str'),
            'value': wrap_language('beans'),
        }

    def test_list(self):
        record = {
            'list': ['a', 'b', 'c'],
        }
        metadata = RecordManifestBuilder._build_metadata(record)
        assert len(metadata) == 1
        assert metadata[0] == {
            'label': wrap_language('list'),
            'value': wrap_language(['a', 'b', 'c']),
        }

    def test_dict(self):
        record = {
            'dict': {'a': 1, 'b': 2},
        }
        metadata = RecordManifestBuilder._build_metadata(record)
        assert len(metadata) == 1
        assert metadata[0] == {
            'label': wrap_language('dict'),
            'value': wrap_language(str({'a': 1, 'b': 2})),
        }

    def test_mix(self):
        record = {
            'int': 40,
            'str': 'beans',
            'list': ['a', 'b', 'c'],
            'dict': {'a': 1, 'b': 2},
        }
        metadata = RecordManifestBuilder._build_metadata(record)
        assert len(metadata) == 4
        assert metadata[0] == {
            'label': wrap_language('int'),
            'value': wrap_language('40'),
        }
        assert metadata[1] == {
            'label': wrap_language('str'),
            'value': wrap_language('beans'),
        }
        assert metadata[2] == {
            'label': wrap_language('list'),
            'value': wrap_language(['a', 'b', 'c']),
        }
        assert metadata[3] == {
            'label': wrap_language('dict'),
            'value': wrap_language(str({'a': 1, 'b': 2})),
        }


class TestBuildCanvas:
    @pytest.mark.ckan_config('ckan.plugins', 'iiif')
    @pytest.mark.usefixtures('with_plugins', 'with_request_context')
    def test_basic(self):
        manifest_id = 'beans/1'
        image_number = 4
        image_id = 'https://some.url/to/the/image'

        canvas = RecordManifestBuilder._build_canvas(
            manifest_id, image_number, image_id
        )

        assert canvas['id'] == toolkit.url_for(
            'iiif.resource',
            identifier=f'{manifest_id}/canvas/{image_number}',
            _external=True,
        )
        assert canvas['type'] == 'Canvas'
        assert canvas['items'][0]['type'] == 'AnnotationPage'
        annotation = canvas['items'][0]['items'][0]
        assert annotation['type'] == 'Annotation'
        assert annotation['motivation'] == 'painting'
        assert annotation['body'] == {'id': image_id, 'type': 'Image'}


class TestGetImages:
    def test_no_image_field(self):
        resource = {}
        record = {}
        images = RecordManifestBuilder._get_images(resource, record)
        assert len(images) == 0

    def test_image_field_but_not_in_record(self):
        resource = {'_image_field': 'images'}
        record = {}
        images = RecordManifestBuilder._get_images(resource, record)
        assert len(images) == 0

    def test_image_field_with_str_no_delimiter(self):
        image_url = 'https://dogr.io/wow/such/test/image.jpg'
        resource = {'_image_field': 'images'}
        record = {'images': image_url}
        images = RecordManifestBuilder._get_images(resource, record)
        assert len(images) == 1
        assert images[0] == image_url

    def test_image_field_with_str_and_delimiter_single(self):
        image_url = 'https://dogr.io/wow/such/test/image.jpg'
        resource = {'_image_field': 'images', '_image_delimiter': ','}
        record = {'images': image_url}
        images = RecordManifestBuilder._get_images(resource, record)
        assert len(images) == 1
        assert images[0] == image_url

    def test_image_field_with_str_and_delimiter_multi(self):
        image_url_1 = 'https://dogr.io/wow/such/test/image.jpg'
        image_url_2 = 'https://dogr.io/wow/second/such/test/image.jpg'
        resource = {'_image_field': 'images', '_image_delimiter': ','}
        record = {'images': f'{image_url_1},{image_url_2}'}
        images = RecordManifestBuilder._get_images(resource, record)
        assert len(images) == 2
        assert images[0] == image_url_1
        assert images[1] == image_url_2

    def test_image_field_with_list_and_delimiter(self):
        # this is an edge case where the user has set a delimiter but then provided an
        # actual list of images. In this case we prioritise the actual value, not the
        # config and so recognise and use the list but ignore the delimiter
        image_url_1 = 'https://dogr.io/wow/such/test/image.jpg'
        image_url_2 = 'https://dogr.io/wow/second/such/test/image.jpg'
        resource = {'_image_field': 'images', '_image_delimiter': ','}
        record = {'images': [image_url_1, image_url_2]}
        images = RecordManifestBuilder._get_images(resource, record)
        assert len(images) == 2
        assert images[0] == image_url_1
        assert images[1] == image_url_2

    def test_image_field_list_of_str(self):
        image_url_1 = 'https://dogr.io/wow/such/test/image.jpg'
        image_url_2 = 'https://dogr.io/wow/second/such/test/image.jpg'
        resource = {'_image_field': 'images'}
        record = {'images': [image_url_1, image_url_2]}
        images = RecordManifestBuilder._get_images(resource, record)
        assert len(images) == 2
        assert images[0] == image_url_1
        assert images[1] == image_url_2

    def test_image_field_list_dict(self):
        image_url_1 = 'https://dogr.io/wow/such/test/image.jpg'
        image_url_2 = 'https://dogr.io/wow/second/such/test/image.jpg'
        resource = {'_image_field': 'images', '_image_delimiter': ','}
        record = {
            'images': [
                {'identifier': image_url_1, 'name': 'Image 1'},
                {'identifier': image_url_2, 'name': 'Image 2'},
            ]
        }
        images = RecordManifestBuilder._get_images(resource, record)
        assert len(images) == 2
        assert images[0] == image_url_1
        assert images[1] == image_url_2


@pytest.mark.usefixtures('clean_db')
class TestBuildRecordManifest:
    @patch(
        'ckanext.iiif.builders.manifest.RecordManifestBuilder._build_record_manifest_id'
    )
    @patch('ckanext.iiif.builders.manifest.RecordManifestBuilder._get_images')
    @patch('ckanext.iiif.builders.manifest.create_id_url')
    @patch('ckanext.iiif.builders.manifest.RecordManifestBuilder._build_label')
    @patch('ckanext.iiif.builders.manifest.RecordManifestBuilder._build_metadata')
    @patch('ckanext.iiif.builders.manifest.RecordManifestBuilder._build_rights')
    @patch('ckanext.iiif.builders.manifest.RecordManifestBuilder._build_canvas')
    def test_manifest_props(
        self,
        canvas_mock,
        rights_mock,
        metadata_mock,
        label_mock,
        create_id_url_mock,
        images_mock,
        record_manifest_id_mock,
    ):
        resource = factories.Resource()
        record_data = {
            '_id': 5,
        }

        images = [MagicMock(), MagicMock()]
        images_mock.configure_mock(return_value=images)
        canvas_mock.configure_mock(side_effect=['first', 'second'])

        mani = RecordManifestBuilder.build_record_manifest(resource, record_data)

        assert images_mock.called
        assert mani['@context'] == 'http://iiif.io/api/presentation/3/context.json'
        assert mani['id'] == create_id_url_mock.return_value
        create_id_url_mock.assert_called_with(record_manifest_id_mock.return_value)
        assert mani['type'] == 'Manifest'
        assert mani['label'] == label_mock.return_value
        assert mani['metadata'] == metadata_mock.return_value
        assert mani['rights'] == rights_mock.return_value
        assert mani['items'] == ['first', 'second']
        assert 'logo' in mani

    @patch('ckanext.iiif.builders.manifest.RecordManifestBuilder._get_images')
    @patch('ckanext.iiif.builders.manifest.RecordManifestBuilder._build_canvas')
    def test_no_images(self, canvas_mock, images_mock):
        resource = factories.Resource()
        record_data = {
            '_id': 5,
        }

        images_mock.configure_mock(return_value=[])
        canvas_mock.configure_mock(side_effect=[])

        with pytest.raises(IIIFBuildError, match='No images found'):
            RecordManifestBuilder.build_record_manifest(resource, record_data)


class TestMatchAndBuildRecordManifest:
    @pytest.mark.parametrize(
        'identifier',
        ['test', 'resource/beans', 'resource/beans/record', 'resource/beans/record/'],
    )
    def test_no_matches(self, identifier):
        builder = RecordManifestBuilder()
        assert builder.match_and_build(identifier) is None

    def test_no_resource(self):
        builder = RecordManifestBuilder()
        with pytest.raises(IIIFBuildError, match='Resource beans not found'):
            builder.match_and_build('resource/beans/record/4')

    @pytest.mark.usefixtures('clean_db')
    def test_no_record(self):
        resource = factories.Resource()

        # TODO: we shouldn't really be mocking the record_show action here but without
        #       adding a dependency on ckanext-nhm where the record_show action is
        #       defined, we're kinda stuck
        record_show_mock = MagicMock(side_effect=NotFound('oh no!'))
        original_get_action = toolkit.get_action

        def get_action(name):
            # we only want to mock record_show, not resource_show, so we have to add
            # some logic here and the hack gets hackier because of it. Dang
            if name == 'record_show':
                return record_show_mock
            else:
                return original_get_action(name)

        get_action_mock = MagicMock(side_effect=get_action)

        with patch(
            'ckanext.iiif.builders.manifest.toolkit.get_action', get_action_mock
        ):
            with pytest.raises(IIIFBuildError, match='Record 4 not found'):
                RecordManifestBuilder().match_and_build(
                    f'resource/{resource["id"]}/record/4'
                )
        record_show_mock.assert_called_once_with(
            {}, {'resource_id': resource['id'], 'record_id': '4'}
        )

    @patch('ckanext.iiif.builders.manifest.toolkit.get_action')
    @patch('ckanext.iiif.builders.manifest.RecordManifestBuilder.build_record_manifest')
    def test_success(self, build_record_manifest_mock, get_action_mock):
        resource = MagicMock()
        record_data = MagicMock()
        record = {'data': record_data}

        action_mock = MagicMock(side_effect=[resource, record])
        get_action_mock.configure_mock(return_value=action_mock)

        RecordManifestBuilder().match_and_build('resource/beans/record/1')

        build_record_manifest_mock.assert_called_once_with(resource, record_data)


class TestBuildIdentifier:
    def test_str_record_id(self):
        resource_id = 'abc'
        record_id = '293'
        builder = RecordManifestBuilder()
        identifier = builder.build_identifier(resource_id, record_id)
        assert identifier == RecordManifestBuilder._build_record_manifest_id(
            resource_id, record_id
        )

    def test_int_record_id(self):
        resource_id = 'abc'
        record_id = 293
        builder = RecordManifestBuilder()
        identifier = builder.build_identifier(resource_id, record_id)
        assert identifier == RecordManifestBuilder._build_record_manifest_id(
            resource_id, record_id
        )
