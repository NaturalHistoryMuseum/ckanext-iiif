import pytest
from ckan.tests import factories
from ckanext.iiif.logic import actions
from unittest.mock import patch, MagicMock, call

from ckanext.iiif.builders.manifest import build_record_manifest
from ckanext.iiif.plugin import IIIFPlugin


@pytest.mark.usefixtures("clean_db")
class TestDatastoreMultisearchModifyResponse:
    def test_success(self):
        plugin = IIIFPlugin()

        resource_1 = factories.Resource()
        resource_2 = factories.Resource()
        record_data_1 = MagicMock()
        record_data_2 = MagicMock()
        record_data_3 = MagicMock()

        response = {
            "records": [
                {"resource": resource_1["id"], "data": record_data_1},
                {"resource": resource_1["id"], "data": record_data_2},
                {"resource": resource_2["id"], "data": record_data_3},
            ]
        }

        mock_build_record_manifest = MagicMock(return_value="yes")

        with patch(
            "ckanext.iiif.plugin.build_record_manifest", mock_build_record_manifest
        ):
            updated_response = plugin.datastore_multisearch_modify_response(response)

        assert all(record["iiif"] == "yes" for record in response["records"])
        assert mock_build_record_manifest.mock_calls == [
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
            "records": [
                {"resource": resource_1["id"], "data": record_data_1},
                {"resource": resource_1["id"], "data": record_data_2},
                {"resource": resource_2["id"], "data": record_data_3},
            ]
        }

        mock_build_record_manifest = MagicMock(side_effect=Exception("oh no!"))

        with patch(
            "ckanext.iiif.plugin.build_record_manifest", mock_build_record_manifest
        ):
            updated_response = plugin.datastore_multisearch_modify_response(response)

        assert all("iiif" not in record for record in response["records"])
        assert mock_build_record_manifest.mock_calls == [
            call(resource_1, record_data_1),
            call(resource_1, record_data_2),
            call(resource_2, record_data_3),
        ]

    def test_complete(self):
        # the other tests mock away build_record_manifest in order to control its
        # behaviour, but we should check that that is being used correctly too so that's
        # what this test does
        plugin = IIIFPlugin()

        resource_1 = factories.Resource()
        record_data = {"_id": 4, "arms": "yes", "length": 15}
        response = {
            "records": [
                {
                    "resource": resource_1["id"],
                    "data": record_data,
                },
            ]
        }

        updated_response = plugin.datastore_multisearch_modify_response(response)
        assert updated_response["records"][0]["iiif"] == build_record_manifest(
            resource_1, record_data
        )


@pytest.mark.usefixtures("clean_db")
class TestConfigure:
    def test_builders_are_hooked(self):
        plugin = IIIFPlugin()

        class MockPlugin:
            def register_iiif_builders(self, builders):
                builders.append("yay!")

        plugin_implementations_mock = MagicMock(return_value=[MockPlugin()])

        with patch(
            "ckanext.iiif.plugin.plugins.PluginImplementations",
            plugin_implementations_mock,
        ):
            plugin.configure(MagicMock())

        assert "yay!" in actions.BUILDERS
