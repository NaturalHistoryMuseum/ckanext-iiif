import pytest
from unittest.mock import patch, MagicMock

from ckanext.iiif.builders.manifest import RecordManifestBuilder
from ckanext.iiif.builders.utils import IIIFBuildError
from ckanext.iiif.logic.actions import build_iiif_resource, build_iiif_identifier


class TestBuildIIIFResource:
    def test_no_builders(self):
        with patch('ckanext.iiif.logic.actions.BUILDERS', {}):
            assert build_iiif_resource('test') is None

    def test_match(self):
        mock_manifest = {'beans': 3}
        mock_builder = MagicMock(match_and_build=MagicMock(return_value=mock_manifest))

        with patch('ckanext.iiif.logic.actions.BUILDERS', {'mock': mock_builder}):
            assert build_iiif_resource('test') is mock_manifest

    def test_no_match(self):
        mock_builder = MagicMock(match_and_build=MagicMock(return_value=None))

        with patch('ckanext.iiif.logic.actions.BUILDERS', {'mock': mock_builder}):
            assert build_iiif_resource('test') is None

    def test_builder_error(self):
        mock_builder = MagicMock(
            match_and_build=MagicMock(side_effect=IIIFBuildError('test', 'oh no!'))
        )

        with patch('ckanext.iiif.logic.actions.BUILDERS', {'mock': mock_builder}):
            assert build_iiif_resource('test') is None

    def test_unhandled_error(self):
        mock_builder = MagicMock(
            match_and_build=MagicMock(side_effect=Exception('oh no!'))
        )

        with patch('ckanext.iiif.logic.actions.BUILDERS', {'mock': mock_builder}):
            with pytest.raises(Exception, match='oh no!'):
                build_iiif_resource('test')

    def test_multiple_builders(self):
        mock_builder_1 = MagicMock(match_and_build=MagicMock(return_value=None))
        mock_builder_2 = MagicMock(match_and_build=MagicMock(return_value=None))
        mock_manifest = {'legs': 489}
        mock_builder_3 = MagicMock(
            match_and_build=MagicMock(return_value=mock_manifest)
        )
        builders = {
            'mock1': mock_builder_1,
            'mock2': mock_builder_2,
            'mock3': mock_builder_3,
        }

        with patch('ckanext.iiif.logic.actions.BUILDERS', builders):
            # first 2 don't match, 3rd one does
            assert build_iiif_resource('test') is mock_manifest

    def test_multiple_builders_all_match(self):
        mock_manifest_1 = {'beans': 3}
        mock_builder_1 = MagicMock(
            match_and_build=MagicMock(return_value=mock_manifest_1)
        )
        mock_manifest_2 = {'arms': 5}
        mock_builder_2 = MagicMock(
            match_and_build=MagicMock(return_value=mock_manifest_2)
        )
        builders = {'mock1': mock_builder_1, 'mock2': mock_builder_2}

        with patch('ckanext.iiif.logic.actions.BUILDERS', builders):
            # should get the first manifest one back
            assert build_iiif_resource('test') is mock_manifest_1

    def test_multiple_builders_with_an_error(self):
        mock_builder_1 = MagicMock(match_and_build=MagicMock(return_value=None))
        mock_builder_2 = MagicMock(
            match_and_build=MagicMock(side_effect=IIIFBuildError('test', 'oh no!'))
        )
        mock_builder_3 = MagicMock(
            match_and_build=MagicMock(return_value={'legs': 489})
        )
        builders = {
            'mock1': mock_builder_1,
            'mock2': mock_builder_2,
            'mock3': mock_builder_3,
        }

        with patch('ckanext.iiif.logic.actions.BUILDERS', builders):
            # first one doesn't match, second throws an error and the other one isn't
            # considered
            assert build_iiif_resource('test') is None


class TestBuildIIIFIdentifier:
    def test_no_builders(self):
        with patch('ckanext.iiif.logic.actions.BUILDERS', {}):
            assert build_iiif_identifier('test', {}) is None

    def test_no_builder_matches(self):
        with patch('ckanext.iiif.logic.actions.BUILDERS', {'mock': MagicMock()}):
            assert build_iiif_identifier('not mock', {}) is None

    def test_success(self):
        builder_id = 'mock'
        mock_identifier = 'hello!'
        mock_builder = MagicMock(
            build_identifier=MagicMock(return_value=mock_identifier)
        )

        with patch('ckanext.iiif.logic.actions.BUILDERS', {builder_id: mock_builder}):
            assert build_iiif_identifier('mock', dict(c=6, x=7)) == mock_identifier

        mock_builder.build_identifier.assert_called_once_with(c=6, x=7)

    def test_wrong_args(self):
        with pytest.raises(TypeError):
            assert build_iiif_identifier(
                RecordManifestBuilder.BUILDER_ID, dict(c=6, x=7)
            )
