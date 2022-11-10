import pytest
from unittest.mock import patch, MagicMock

from ckanext.iiif.builders.utils import IIIFBuildError
from ckanext.iiif.logic.actions import build_iiif_resource


class TestBuildIIIFResource:
    def test_no_builders(self):
        with patch("ckanext.iiif.logic.actions.BUILDERS", {}):
            assert build_iiif_resource("test") is None

    def test_match(self):
        mock_manifest = {"beans": 3}
        mock_builder = MagicMock(return_value=mock_manifest)

        with patch("ckanext.iiif.logic.actions.BUILDERS", {"mock": mock_builder}):
            assert build_iiif_resource("test") is mock_manifest

    def test_no_match(self):
        mock_builder = MagicMock(return_value=None)

        with patch("ckanext.iiif.logic.actions.BUILDERS", {"mock": mock_builder}):
            assert build_iiif_resource("test") is None

    def test_builder_error(self):
        mock_builder = MagicMock(side_effect=IIIFBuildError("test", "oh no!"))

        with patch("ckanext.iiif.logic.actions.BUILDERS", {"mock": mock_builder}):
            assert build_iiif_resource("test") is None

    def test_unhandled_error(self):
        mock_builder = MagicMock(side_effect=Exception("oh no!"))

        with patch("ckanext.iiif.logic.actions.BUILDERS", {"mock": mock_builder}):
            with pytest.raises(Exception, match="oh no!"):
                build_iiif_resource("test")

    def test_multiple_builders(self):
        mock_builder_1 = MagicMock(return_value=None)
        mock_builder_2 = MagicMock(return_value=None)
        mock_manifest = {"legs": 489}
        mock_builder_3 = MagicMock(return_value=mock_manifest)
        builders = {
            "mock1": mock_builder_1,
            "mock2": mock_builder_2,
            "mock3": mock_builder_3,
        }

        with patch("ckanext.iiif.logic.actions.BUILDERS", builders):
            # first 2 don't match, 3rd one does
            assert build_iiif_resource("test") is mock_manifest

    def test_multiple_builders_all_match(self):
        mock_manifest_1 = {"beans": 3}
        mock_builder_1 = MagicMock(return_value=mock_manifest_1)
        mock_manifest_2 = {"arms": 5}
        mock_builder_2 = MagicMock(return_value=mock_manifest_2)
        builders = {"mock1": mock_builder_1, "mock2": mock_builder_2}

        with patch("ckanext.iiif.logic.actions.BUILDERS", builders):
            # should get the first manifest one back
            assert build_iiif_resource("test") is mock_manifest_1

    def test_multiple_builders_with_an_error(self):
        mock_builder_1 = MagicMock(return_value=None)
        mock_builder_2 = MagicMock(side_effect=IIIFBuildError("test", "oh no!"))
        mock_builder_3 = MagicMock(return_value={"legs": 489})
        builders = {
            "mock1": mock_builder_1,
            "mock2": mock_builder_2,
            "mock3": mock_builder_3,
        }

        with patch("ckanext.iiif.logic.actions.BUILDERS", builders):
            # first one doesn't match, second throws an error and the other one isn't
            # considered
            assert build_iiif_resource("test") is None
