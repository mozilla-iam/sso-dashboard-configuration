#!/bin/bash

TRIGGER=${CODEBUILD_WEBHOOK_TRIGGER:-${MANUAL_DEPLOY_TRIGGER:-}}

echo "Begin deploy of the apps.yml file."
echo "Webhook trigger: ${CODEBUILD_WEBHOOK_TRIGGER:-None}"
echo "Manual deploy trigger: ${MANUAL_DEPLOY_TRIGGER:-None}"
echo "Effective trigger: $TRIGGER"

if [[ "$TRIGGER" == "branch/master" ]]; then
		echo "Deploying to the development CDN cdn.sso.allizom.org"
        make deploy S3_BUCKET=sso-dashboard.configuration
elif [[ "$TRIGGER" =~ ^tag\/[0-9]+\.[0-9]+\.[0-9]+(\-(prod))?$ ]]; then
		echo "Deploying to the production CDN cdn.sso.mozilla.com"
        make deploy S3_BUCKET=sso-dashboard.configuration-prod
fi

echo "End deploy of the apps.yml."
