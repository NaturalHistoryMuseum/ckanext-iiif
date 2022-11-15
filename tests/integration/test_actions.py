import pytest
from ckan.plugins import toolkit
from unittest.mock import MagicMock, patch

from ckanext.iiif.builders.manifest import RecordManifestBuilder


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
        mock_builder = MagicMock(match_and_build=MagicMock(return_value=mock_manifest))

        build_iiif_resource = toolkit.get_action("build_iiif_resource")

        with patch("ckanext.iiif.logic.actions.BUILDERS", {"mock": mock_builder}):
            assert build_iiif_resource({}, {"identifier": "test"}) == mock_manifest

    def test_no_match(self):
        mock_builder = MagicMock(match_and_build=MagicMock(return_value=None))

        build_iiif_resource = toolkit.get_action("build_iiif_resource")

        with patch("ckanext.iiif.logic.actions.BUILDERS", {"mock": mock_builder}):
            assert build_iiif_resource({}, {"identifier": "test"}) is None


@pytest.mark.ckan_config("ckan.plugins", "iiif")
@pytest.mark.usefixtures("with_plugins")
class TestBuildIIIFIdentifier:
    """
    Tests that check the action function is correctly installed as part of the IIIF
    plugin and then can be used correctly when get_action is used and it is called.

    Because the unit tests cover off checking various scenarios work, these tests just
    check two simple examples and nothing more.
    """

    def test_no_builders(self):
        build_iiif_identifier = toolkit.get_action("build_iiif_identifier")

        with patch("ckanext.iiif.logic.actions.BUILDERS", {}):
            assert build_iiif_identifier({}, {"builder_id": "test"}) is None

    def test_correct_args(self):
        builder_id = "mock"
        mock_identifier = "hello!"
        mock_builder = MagicMock(
            build_identifier=MagicMock(return_value=mock_identifier)
        )

        build_iiif_identifier = toolkit.get_action("build_iiif_identifier")

        with patch("ckanext.iiif.logic.actions.BUILDERS", {builder_id: mock_builder}):
            assert (
                build_iiif_identifier({}, {"builder_id": builder_id}) == mock_identifier
            )

    def test_wrong_args(self):
        build_iiif_identifier = toolkit.get_action("build_iiif_identifier")

        with pytest.raises(TypeError):
            build_iiif_identifier(
                {}, {"builder_id": RecordManifestBuilder.BUILDER_ID, "bananas": 63}
            )
