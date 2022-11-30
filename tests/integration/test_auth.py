import pytest
from ckan.plugins import toolkit
from ckan.tests import factories


@pytest.mark.filterwarnings('ignore::sqlalchemy.exc.SADeprecationWarning')
@pytest.mark.ckan_config('ckan.plugins', 'iiif')
@pytest.mark.usefixtures('clean_db', 'with_plugins', 'with_request_context')
class TestBuildIIIFResource:
    """
    Tests that check the auth function is correctly installed as part of the IIIF plugin
    and then can be used correctly when check_access is called.
    """

    def test_no_user(self):
        assert toolkit.check_access('build_iiif_resource', {})

    def test_user(self):
        user = factories.User()
        assert toolkit.check_access('build_iiif_resource', {'user': user['name']})

    def test_sysadmin(self):
        user = factories.Sysadmin()
        assert toolkit.check_access('build_iiif_resource', {'user': user['name']})
