"Test the YAML file is loadable and valid"
import logging
import unittest
import yaml


logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


class YAMLTest(unittest.TestCase):
    def get_yaml_file(self):
        apps_yml = open('apps.yml')
        contents = apps_yml.read()
        apps_yml.close()
        return contents

    def test_output_exists(self):
        assert self.get_yaml_file() is not None

    def test_yaml_loads(self):
        yaml_content = yaml.load(self.get_yaml_file())
        assert yaml_content is not None

    def test_each_has_required_keys(self):
        yaml_content = yaml.load(self.get_yaml_file())
        assert yaml_content is not None

        for app in yaml_content['apps']:
            logger.info('Validating keys for {}'.format(app['application']))
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
