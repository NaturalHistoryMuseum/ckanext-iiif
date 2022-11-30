from unittest.mock import MagicMock

from ckanext.iiif.logic.auth import build_iiif_resource, build_iiif_identifier


class TestBuildIIIFResource:
    def test_always_success(self):
        assert build_iiif_resource(MagicMock(), MagicMock())['success']


class TestBuildIIIFIdentifier:
    def test_always_success(self):
        assert build_iiif_identifier(MagicMock(), MagicMock())['success']
