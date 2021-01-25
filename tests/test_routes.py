import pytest
import re
from mock import patch, MagicMock, call

from ckanext.iiif.routes.iiif import resource


def test_no_builders():
    # TODO: it would be nicer to not mock the toolkit.abort function and just use pytest.raises on
    #       the HTTPException that it raises, but I can't get that to work :(
    mock_builders = {}
    mock_toolkit = MagicMock(abort=MagicMock(side_effect=Exception('yep')))

    with patch('ckanext.iiif.routes.iiif.builders', mock_builders):
        with patch('ckanext.iiif.routes.iiif.toolkit', mock_toolkit):
            with pytest.raises(Exception, match='yep'):
                resource(MagicMock())

    assert mock_toolkit.abort.call_args == call(status_code=404, detail='Unknown IIIF identifier')


@pytest.mark.filterwarnings('ignore::sqlalchemy.exc.SADeprecationWarning')
@pytest.mark.usefixtures('with_request_context')
def test_match():
    identifier = 'resource/1/record/1'

    mock_get_builder = MagicMock(return_value=MagicMock(build=MagicMock(return_value={})))
    mock_builders = {
        re.compile('resource/(?P<resource_id>.+?)/record/(?P<record_id>.+)$'): mock_get_builder
    }

    with patch('ckanext.iiif.routes.iiif.builders', mock_builders):
        response = resource(identifier)

    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    assert response.data.strip() == b'{}'
    assert mock_get_builder.call_args == call(resource_id='1', record_id='1')
