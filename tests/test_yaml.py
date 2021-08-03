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
        self.assertIsNotNone(self.get_yaml_file(), msg='Loading apps.yml failed')

    def test_yaml_loads(self):
        ''' Verify that apps.yml is valid yaml '''
        yaml_content = yaml.load(self.get_yaml_file(), Loader=yaml.FullLoader)
        self.assertIsNotNone(yaml_content, msg='apps.yml is structurally invalid YAML')

    def test_each_has_required_keys(self):
        ''' Verify that apps.yml has keys we expect '''
        yaml_content = yaml.load(self.get_yaml_file(), Loader=yaml.FullLoader)
        self.assertIsNotNone(yaml_content, msg='apps.yml is structurally invalid YAML')
        # The YAML is a key of the literal word 'apps' ...
        self.assertIn('apps', yaml_content, msg='apps.yml has no "apps" key')

        # ... whose values are a list of entries ...
        for app_entry in yaml_content.get('apps', []):
            # ... where each entry is key'ed as the literal word 'application':
            app = app_entry.get('application', {})
            # And each entry has keys, which we'll now look at.

            # First, let's look at the name, because otherwise, we'll be super spammy when
            # we report on what we're looking at:
            appname = app.get('name')
            if appname is None:
                logger.info(('There is an entry without a name in app %s.'
                             'This is so broken I am stopping analyzing it.'), app)
                continue

            # Now, investigate the rest of the keys that must be present:
            logger.info('Validating keys for %s', appname)
            for attribute in ['op', 'url', 'logo', 'authorized_users', 'authorized_groups',
                              'display']:
                self.assertIsNotNone(app.get(attribute),
                                     msg=f'{appname} is missing a "{attribute}" attribute')

            # Finally, inspect the keys that are "if they're here, must be a certain way":
            self.assertIsInstance(app.get('display'), bool)

            if app.get('client_id') is not None:
                # client_id is not required, but maybe should be, see
                # https://github.com/mozilla-iam/sso-dashboard-configuration/pull/371
                self.assertRegex(app['client_id'], r'^[A-Za-z0-9]{32}$',
                                 msg=f'{appname} has a malformed client_id')
                if not (app.get('authorized_groups') or app.get('authorized_users')):
                    logger.warning(('%s has a client_id but no auth layers defined.  '
                                     'Verify this is correct.'), appname)
            else:
                logger.warning(('%s has no client_id, everyone has access.  '
                                'Verify this is correct.'), appname)

            if app.get('expire_access_when_unused_after') is not None:
                self.assertIsInstance(app['expire_access_when_unused_after'], int)
