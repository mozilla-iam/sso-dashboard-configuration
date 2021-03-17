#!/bin/bash

echo "Begin deploy of the apps.yml file."
echo "$CODEBUILD_WEBHOOK_TRIGGER"


if [[ "branch/master" == "$CODEBUILD_WEBHOOK_TRIGGER" ]]
	then
		echo "Deploying to the development CDN cdn.sso.allizom.org"
        make deploy S3_BUCKET=sso-dashboard.configuration
elif [[ "$CODEBUILD_WEBHOOK_TRIGGER" =~ ^tag\/[0-9]+\.[0-9]+\.[0-9]+(\-(prod))?$ ]]
	then
		echo "Deploying to the production CDN cdn.sso.mozilla.com"
        make deploy S3_BUCKET=sso-dashboard.configuration-prod
fi


echo "$CODEBUILD_WEBHOOK_TRIGGER"
echo "End deploy of the apps.yml."
