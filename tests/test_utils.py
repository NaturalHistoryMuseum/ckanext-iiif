from ckanext.iiif.lib.utils import wrap_language
from mock import MagicMock


def test_wrap_language():
    test_value = MagicMock()

    assert wrap_language(test_value) == {'en': [test_value]}
    assert wrap_language([test_value]) == {'en': [test_value]}
    assert wrap_language(test_value, language='beans') == {'beans': [test_value]}
