import pytest
from flask import Response
from unittest.mock import patch, MagicMock

from ckanext.iiif.routes.iiif import blueprint, resource


@pytest.mark.ckan_config('ckan.plugins', 'iiif')
@pytest.mark.usefixtures('with_plugins', 'with_request_context')
class TestIIIFRoute:
    def test_blueprint(self):
        assert blueprint.name == 'iiif'
        assert blueprint.url_prefix == '/iiif'

    def test_result(self):
        mock_manifest = {'limbs': True}
        mock_builder = MagicMock(match_and_build=MagicMock(return_value=mock_manifest))

        with patch('ckanext.iiif.logic.actions.BUILDERS', {'mock': mock_builder}):
            response: Response = resource('test')

        assert response.content_type == 'application/json'
        assert response.status_code == 200
        assert response.json == mock_manifest

    def test_no_result(self):
        mock_builder = MagicMock(match_and_build=MagicMock(return_value=None))
        # I'm mocking abort here because of some issues getting Flask in the test env
        # to work when calling CKAN's abort (which gets converted into a Werkzeug
        # NotFound). It seems to want a secret_key and I couldn't make it to work so
        # this does the job! We still have an integration test which tests that you do
        # get a proper 404 error when you use the Flask test client so this feels ok
        mock_abort = MagicMock(return_value=MagicMock())

        with patch('ckanext.iiif.logic.actions.BUILDERS', {'mock': mock_builder}):
            with patch('ckanext.iiif.routes.iiif.toolkit.abort', mock_abort):
                assert resource('test') is mock_abort.return_value

        mock_abort.assert_called_with(status_code=404, detail='Unknown IIIF identifier')
