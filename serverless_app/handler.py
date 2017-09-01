import boto3
import credstash
import datetime
import logging
import os
import time
import yaml


logger = logging.getLogger(__name__)


class Configuration(object):

    def get_secret(self, secret_name, context):
        """Fetch secret from environment or credstash."""
        secret = os.getenv(secret_name, None)

        if secret is None:
            secret = credstash.getSecret(
                name=secret_name,
                context=context,
                region="us-east-1"
            )
        return secret


class CloudFront(Configuration):
    def __init__(self):
        self.cloudfront = None

    def connect(self):
        if not self.cloudfront:
            self.cloudfront = boto3.client('cloudfront')

    @property
    def distribution(self):
        return self.get_secret('sso-dashboard.cloudfront_distribution', {'app': 'sso-dashboard'})

    def invalidate_images(self, key):
        self.connect()
        response = self.cloudfront.create_invalidation(
            DistributionId=self.distribution,
            InvalidationBatch={
                'Paths': {
                    'Quantity': 1,
                    'Items': [
                        '/images/{key}'.format(key=key)
                    ]
                },
                'CallerReference': str(time.time())
            }
        )
        return response


class DashboardConfiguration(Configuration):
    def __init__(self):
        self.dynamodb = None
        self.s3 = None

    def connect_dyanmo(self):
        if not self.dynamodb:
            self.dynamodb = boto3.resource('dynamodb')
            self.table = self.dynamodb.Table('sso-dashboard-apps')

    def connect_s3(self):
        if not self.s3:
            self.s3 = boto3.client('s3')

    @property
    def s3_bucket(self):
        return self.get_secret('sso-dashboard.s3_bucket', {'app': 'sso-dashboard'})

    @property
    def apps_yaml(self):
        self.connect_s3()
        yaml_file = self.s3.get_object(
            Bucket=self.s3_bucket,
            Key='apps.yml'
        )

        return yaml.safe_load(yaml_file['Body'].read())

    def needs_update(self, app_name, app):
        self.connect_dyanmo()

        resp = self.table.get_item(
            Key={'name': app_name}
        ).get('Item')

        if resp is not None:
            for k,v in resp.items():
                if v == (app.get(k)):
                    continue
                else:
                    return True
            return False
        return True

    def update(self):
        self.connect_dyanmo()
        now = int(datetime.datetime.now().strftime("%s")) * 1000
        updated = 0
        for app in self.apps_yaml.get('apps'):

            application = app.get('application')

            if self.needs_update(app_name=application.get('name'), app=application):
                application['last_updated'] = now
                self.table.put_item(
                    Item=application
                )
                CloudFront().invalidate_images(application.get('logo'))
                updated = updated + 1

        return updated

def lambda_handler(event=None, context=None):

    d = DashboardConfiguration()
    apps_updated = d.update()

    response = {
        "statusCode": 200,
        "body": ''
    }

    return response
