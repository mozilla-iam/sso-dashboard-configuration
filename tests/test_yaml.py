"Test the YAML file is loadable and valid"
import logging
import unittest
import yaml


logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


class YAMLTest(unittest.TestCase):
    ''' Class that tests the apps.yml file for the SSO Dashboard '''
    @staticmethod
    def get_yaml_file():
        ''' fetch the contents of apps.yml as one big blob '''
        with open('apps.yml') as apps_yml:
            contents = apps_yml.read()
        return contents

    def test_output_exists(self):
        ''' Verify that apps.yml is present '''
        assert self.get_yaml_file() is not None

    def test_yaml_loads(self):
        ''' Verify that apps.yml is valid yaml '''
        yaml_content = yaml.load(self.get_yaml_file())
        assert yaml_content is not None

    def test_each_has_required_keys(self):
        ''' Verify that apps.yml has keys we expect '''
        yaml_content = yaml.load(self.get_yaml_file())
        assert yaml_content is not None

        for app in yaml_content['apps']:
            logger.info('Validating keys for %s', app['application'])
            assert app['application']['name'] is not None
            # assert app['application']['client_id'] is not None # Client ID not required
            assert app['application']['op'] is not None
            assert app['application']['url'] is not None
            assert app['application']['logo'] is not None
            assert app['application']['authorized_users'] is not None
            assert app['application']['authorized_groups'] is not None
            assert app['application']['display'] is not None
            if app['application'].get('expire_access_when_unused_after') is not None:
                assert isinstance(app['application']['expire_access_when_unused_after'], int)
