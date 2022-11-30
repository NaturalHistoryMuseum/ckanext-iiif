import pytest
from ckan.tests import factories
from unittest.mock import patch, MagicMock, call

from ckanext.iiif.builders.manifest import RecordManifestBuilder
from ckanext.iiif.logic import actions
from ckanext.iiif.plugin import IIIFPlugin


@pytest.mark.usefixtures('clean_db')
class TestDatastoreMultisearchModifyResponse:
    def test_success(self):
        plugin = IIIFPlugin()

        resource_1 = factories.Resource()
        resource_2 = factories.Resource()
        record_data_1 = MagicMock()
        record_data_2 = MagicMock()
        record_data_3 = MagicMock()

        response = {
            'records': [
                {'resource': resource_1['id'], 'data': record_data_1},
                {'resource': resource_1['id'], 'data': record_data_2},
                {'resource': resource_2['id'], 'data': record_data_3},
            ]
        }

        mock_record_manifest_builder = MagicMock(
            build_record_manifest=MagicMock(return_value='yes')
        )

        with patch(
            'ckanext.iiif.plugin.RecordManifestBuilder', mock_record_manifest_builder
        ):
            updated_response = plugin.datastore_multisearch_modify_response(response)

        assert all(record['iiif'] == 'yes' for record in updated_response['records'])
        assert mock_record_manifest_builder.build_record_manifest.mock_calls == [
            call(resource_1, record_data_1),
            call(resource_1, record_data_2),
            call(resource_2, record_data_3),
        ]

    def test_error_suppression(self):
        plugin = IIIFPlugin()

        resource_1 = factories.Resource()
        resource_2 = factories.Resource()
        record_data_1 = MagicMock()
        record_data_2 = MagicMock()
        record_data_3 = MagicMock()

        response = {
            'records': [
                {'resource': resource_1['id'], 'data': record_data_1},
                {'resource': resource_1['id'], 'data': record_data_2},
                {'resource': resource_2['id'], 'data': record_data_3},
            ]
        }

        mock_record_manifest_builder = MagicMock(
            build_record_manifest=MagicMock(side_effect=Exception('oh no!'))
        )

        with patch(
            'ckanext.iiif.plugin.RecordManifestBuilder',
            mock_record_manifest_builder,
        ):
            updated_response = plugin.datastore_multisearch_modify_response(response)

        assert all('iiif' not in record for record in updated_response['records'])
        assert mock_record_manifest_builder.build_record_manifest.mock_calls == [
            call(resource_1, record_data_1),
            call(resource_1, record_data_2),
            call(resource_2, record_data_3),
        ]

    def test_complete(self):
        # the other tests mock away build_record_manifest in order to control its
        # behaviour, but we should check that that is being used correctly too so that's
        # what this test does
        plugin = IIIFPlugin()

        resource_1 = factories.Resource(_image_field='images')
        record_data = {
            '_id': 4,
            'arms': 'yes',
            'length': 15,
            'images': ['https://image.com/image.jpg'],
        }
        response = {
            'records': [
                {
                    'resource': resource_1['id'],
                    'data': record_data,
                },
            ]
        }

        updated_response = plugin.datastore_multisearch_modify_response(response)
        assert updated_response['records'][0][
            'iiif'
        ] == RecordManifestBuilder.build_record_manifest(resource_1, record_data)


@pytest.mark.usefixtures('clean_db')
class TestConfigure:
    def test_builders_are_hooked(self):
        plugin = IIIFPlugin()

        class MockPlugin:
            def register_iiif_builders(self, builders):
                builders['test'] = 'yay!'

        plugin_implementations_mock = MagicMock(return_value=[MockPlugin()])

        with patch(
            'ckanext.iiif.plugin.plugins.PluginImplementations',
            plugin_implementations_mock,
        ):
            plugin.configure(MagicMock())

        assert actions.BUILDERS['test'] == 'yay!'
