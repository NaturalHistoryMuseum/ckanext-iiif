import pytest
from ckanext.iiif.lib.utils import wrap_language, create_image_server_url
from mock import MagicMock


@pytest.mark.ckan_config(u'ckanext.iiif.image_server_url', u'https://something.com')
def test_create_image_server_url():
    result = create_image_server_url(u'an_identifier!', identifier_type=u'a_type!')
    assert result == u'https://something.com/a_type!:an_identifier!'


def test_wrap_language():
    test_value = MagicMock()

    assert wrap_language(test_value) == {u'en': [test_value]}
    assert wrap_language([test_value]) == {u'en': [test_value]}
    assert wrap_language(test_value, language=u'beans') == {u'beans': [test_value]}
