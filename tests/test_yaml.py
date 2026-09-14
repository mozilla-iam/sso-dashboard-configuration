"Test the YAML file is loadable and valid"
import logging
import os.path
import unittest
import re
from typing import Literal, NotRequired, TypedDict
from urllib.parse import urlparse

import ruamel.yaml
from typeguard import check_type


logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


# These specs also live, albiet potentially paraphrased, in
# sso-dashboard/dashboard/models/apps.py.

class StepUp(TypedDict):
    """
    This is the canonical type definition. The one in sso-dashboard is not,
    because it only cares about presentation. The intended consumer of YAML
    validated by this is auth0-deploy.

    The spec in sso-dashboard leaves `required_indicator` unconstrained,
    because it doesn't need to care about indicators. We have a stricter
    definition here to prevent sending garbage to auth0-deploy.
    """
    matching_users: list[str]
    matching_groups: list[str]
    # Documented in the README.
    required_indicator: Literal["WEBAUTHN", "ROAMAUTH"]

# Change these definitions in sso-dashboard first, and then make the changes
# here.
class Application(TypedDict):
    """
    Canonically defined in the SSO Dashboard, except for `step_up`, which is
    defined above.
    """
    name: str
    # They are all 'auth0' currently but that might change someday.
    op: Literal["auth0"]
    url: str
    logo: str
    display: bool
    authorized_users: list[str]
    authorized_groups: list[str]
    client_id: NotRequired[str]
    vanity_url: NotRequired[list[str]]
    AAL: NotRequired[Literal["LOW", "MEDIUM", "HIGH", "MAXIMUM"]]
    step_up: NotRequired[StepUp]

class AppEntry(TypedDict):
    """An item in the `apps` list."""
    application: Application

class Apps(TypedDict):
    """The top-level definition of the apps.yml"""
    apps: list[AppEntry]


def get_yaml_file() -> Apps:
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
            # Every app_entry is a (key) literal 'application' string ...
            assert 'application' in app_entry
            app = app_entry['application']
            logger.info('Validating keys for %s', app)

            # Validate using our schema.
            check_type(app, Application)

            # This regex is fair game for modifications, it's just to require thoughtful adds.
            assert re.match(r'^[- A-Za-z0-9.():@/,]+$', app['name'])

            # Client ID not required, but is validated if present.
            if 'client_id' in app:
                assert re.match(r'^[A-Za-z0-9]{32}$', app['client_id'])

            # Ensure we're redirecting to a URL.
            assert urlparse(app['url']).scheme in ["http", "https"]

            # Ensure the logo exists in this repository, and is formatted nicely.
            assert re.match(r'^[-_A-Za-z0-9.]+$', app['logo'])
            assert os.path.exists(f"images/{app['logo']}")

            # Quick and hacky way to validate emails.
            for auth_user_raw in app['authorized_users']:
                assert re.match(r'^[-_A-Za-z0-9.@+]+$', auth_user_raw)

            # Should match either a LDAP or Mozillians group.
            for auth_group_raw in app['authorized_groups']:
                assert isinstance(auth_group_raw, str)
                assert re.match(r'^[-_A-Za-z0-9]+$', auth_group_raw)

            if 'vanity_url' in app:
                # deliberate 'test-then-get' to detect a case of "key but no value" as
                # opposed to .get() returning a None.
                vanity_urls_raw = app['vanity_url']
                # Keep it a little pretty, no empty lists.
                assert len(vanity_urls_raw) > 0
                for vanity_url_raw in vanity_urls_raw:
                    assert re.match(r'^/[-_A-Za-z0-9]+$', vanity_url_raw)

            # Same validation as authorized_users / authorized_groups.
            if step_up := app.get('step_up', {}):
                assert app['client_id'], "Step-up only works for apps which hit Auth0"
                for user in step_up.get('matching_users', []):
                    assert re.match(r'^[-_A-Za-z0-9.@+]+$', user)
                for group in step_up.get('matching_groups', []):
                    assert re.match(r'^[-_A-Za-z0-9.@+]+$', group)

    def test_each_app_has_one_aal(self):
        apps = {}
        yaml_content = get_yaml_file()
        for app_entry in yaml_content['apps']:
            app = app_entry['application']
            client_id = app.get("client_id")
            if client_id is None:
                continue
            aal = app.get("AAL", "MEDIUM")
            if client_id not in apps:
                apps[client_id] = aal
                continue
            assert apps[client_id] == aal, f"double AAL for same client id {client_id}"

    def test_each_app_has_one_step_up(self):
        """
        The Access Provider stops at the first entry which authorizes the user,
        so duplicate entries for a client must agree on step_up.
        """
        apps = {}
        yaml_content = get_yaml_file()
        for app_entry in yaml_content['apps']:
            app = app_entry['application']
            client_id = app.get("client_id")
            if client_id is None:
                continue
            step_up = app.get("step_up")
            if client_id not in apps:
                apps[client_id] = step_up
                continue
            assert apps[client_id] == step_up, f"differing step_up for same client id {client_id}"
