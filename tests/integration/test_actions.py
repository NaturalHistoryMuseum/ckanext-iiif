import pytest
from ckan.plugins import toolkit
from unittest.mock import MagicMock, patch


@pytest.mark.ckan_config("ckan.plugins", "iiif")
@pytest.mark.usefixtures("with_plugins")
class TestBuildIIIFResource:
    """
    Tests that check the action function is correctly installed as part of the IIIF
    plugin and then can be used correctly when get_action is used and it is called.

    Because the unit tests cover off checking various scenarios work, these tests just
    check two simple examples and nothing more.
    """

    def test_match(self):
        mock_manifest = {"beans": 3}
        mock_builder = MagicMock(return_value=mock_manifest)

        build_iiif_resource = toolkit.get_action("build_iiif_resource")

        with patch("ckanext.iiif.logic.actions.BUILDERS", [mock_builder]):
            assert build_iiif_resource({}, {"identifier": "test"}) == mock_manifest

    def test_no_match(self):
        mock_builder = MagicMock(return_value=None)

        build_iiif_resource = toolkit.get_action("build_iiif_resource")

        with patch("ckanext.iiif.logic.actions.BUILDERS", [mock_builder]):
            assert build_iiif_resource({}, {"identifier": "test"}) is None
