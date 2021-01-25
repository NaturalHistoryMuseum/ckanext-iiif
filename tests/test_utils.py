import pytest
from mock import MagicMock

from ckanext.iiif.lib.utils import wrap_language, create_image_server_url


@pytest.mark.ckan_config('ckanext.iiif.image_server_url', 'https://something.com')
def test_create_image_server_url():
    result = create_image_server_url('an_identifier!', identifier_type='a_type!')
    assert result == 'https://something.com/a_type!:an_identifier!'


def test_wrap_language():
    test_value = MagicMock()

    assert wrap_language(test_value) == {'en': [test_value]}
    assert wrap_language([test_value]) == {'en': [test_value]}
    assert wrap_language(test_value, language='beans') == {'beans': [test_value]}
