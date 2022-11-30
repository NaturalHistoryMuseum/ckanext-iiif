from ckanext.iiif.builders.utils import wrap_language
from mock import MagicMock


def test_wrap_language():
    # use a mock to test that nothing gets changed (i.e. the function doesn't try to
    # convert the value to a string)
    test_value = MagicMock()

    assert wrap_language(test_value) == {'none': [test_value]}
    assert wrap_language([test_value]) == {'none': [test_value]}
    assert wrap_language(test_value, language='beans') == {'beans': [test_value]}
