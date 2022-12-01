import json

import pytest
from unittest.mock import patch, MagicMock, call


@pytest.mark.ckan_config('ckan.plugins', 'iiif')
@pytest.mark.usefixtures('with_plugins', 'with_request_context')
class TestIIIFRoute:
    """
    Test the /iiif route through the test app to make sure it is plumbed by the plugin
    correctly.
    """

    def test_no_builders(self, app):
        with patch('ckanext.iiif.logic.actions.BUILDERS', {}):
            response = app.get('/iiif/dummy')
        assert response.status_code == 404

    def test_match(self, app):
        identifier = 'resource/1/record/1'
        mock_manifest = {'beans': 3}
        mock_builder = MagicMock(match_and_build=MagicMock(return_value=mock_manifest))

        with patch('ckanext.iiif.logic.actions.BUILDERS', {'mock': mock_builder}):
            response = app.get(f'/iiif/{identifier}')

        assert response.status_code == 200
        assert response.mimetype == 'application/json'
        assert json.loads(response.data) == mock_manifest
        assert mock_builder.match_and_build.call_args == call(identifier)

    def test_no_match(self, app):
        identifier = 'resource/1/record/1'
        mock_builder = MagicMock(match_and_build=MagicMock(return_value=None))

        with patch('ckanext.iiif.logic.actions.BUILDERS', {'mock': mock_builder}):
            response = app.get(f'/iiif/{identifier}')

        assert response.status_code == 404
