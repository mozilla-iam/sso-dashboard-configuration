"Test the YAML file is loadable and valid"
import logging
import os.path
import unittest
import re
import ruamel.yaml


logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


def get_yaml_file():
    yaml = ruamel.yaml.YAML()
    with open('apps.yml', encoding='utf-8') as apps_yml:
        return yaml.load(apps_yml)

class YAMLTest(unittest.TestCase):

    def test_yaml_loads(self):
        yaml_content = get_yaml_file()
        assert yaml_content is not None

    def test_each_has_required_keys(self):
        yaml_content = get_yaml_file()

        for app_entry in yaml_content['apps']:
            ####################################################################################
            # Every app_entry is a (key) literal 'application' string ...
            assert 'application' in app_entry
            app = app_entry['application']
            logger.info('Validating keys for %s', app)
            ####################################################################################
            # ... whose value is a dict ...
            assert isinstance(app, dict)
            # ... the values of which also need validating.
            ####################################################################################
            assert app['name'] is not None
            assert isinstance(app['name'], str)
            # This regex is fair game for modifications, it's just to require thoughtful adds
            assert re.match(r'^[- A-Za-z0-9.():@/]+$', app['name'])
            ####################################################################################
            if 'AAL' in app:
                assert isinstance(app['AAL'], str)
                assert re.match(r'^(LOW|MEDIUM)$', app['AAL'])
            ####################################################################################
            # Client ID not required, but is validated if present
            if 'client_id' in app:
                assert isinstance(app['client_id'], str)
                assert re.match(r'^[A-Za-z0-9]{32}$', app['client_id'])
            ####################################################################################
            assert app['op'] is not None
            assert isinstance(app['op'], str)
            assert len(app['op']) > 0
            # They are all 'auth0' currently but that might change someday.
            assert re.match(r'^auth0$', app['op'])
            ####################################################################################
            assert 'url' in app
            assert isinstance(app['url'], str)
            assert re.match(r'^https?://', app['url'])
            ####################################################################################
            assert 'logo' in app
            assert isinstance(app['logo'], str)
            assert re.match(r'^[-_A-Za-z0-9.]+$', app['logo'])
            assert os.path.exists(f"images/{app['logo']}")
            ####################################################################################
            assert app['authorized_users'] is not None
            assert isinstance(app['authorized_users'], list)
            for auth_user_raw in app['authorized_users']:
                assert isinstance(auth_user_raw, str)
                assert re.match(r'^[-_A-Za-z0-9.@+]+$', auth_user_raw)
            ####################################################################################
            assert app['authorized_groups'] is not None
            assert isinstance(app['authorized_groups'], list)
            for auth_group_raw in app['authorized_groups']:
                assert isinstance(auth_group_raw, str)
                assert re.match(r'^[-_A-Za-z0-9]+$', auth_group_raw)
            ####################################################################################
            assert app['display'] is not None
            assert isinstance(app['display'], bool)
            ####################################################################################
            if 'vanity_url' in app:
                # deliberate 'test-then-get' to detect a case of "key but no value" as
                # opposed to .get() returning a None.
                vanity_urls_raw = app['vanity_url']
                assert isinstance(vanity_urls_raw, list)
                assert len(vanity_urls_raw) > 0
                for vanity_url_raw in vanity_urls_raw:
                    assert isinstance(vanity_url_raw, str)
                    assert re.match(r'^/[-_A-Za-z0-9]+$', vanity_url_raw)
            ####################################################################################
