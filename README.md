# sso-dashboard-configuration

[![Build Status](https://travis-ci.org/mozilla-iam/sso-dashboard-configuration.svg?branch=master)](https://travis-ci.org/mozilla-iam/sso-dashboard-configuration)

# How it works...

The apps.yml controls app visibility in the dashboard based on group membership
or lists of users.  

Groups are simple _name of group_.  Users are identified by their `primaryEmail`.
`expire_access_when_unused_after` is used to expire access to a relying party automatically after the said time in
seconds.

# Git workflow

In order to publish a change you must:

1. Clone the repository
2. Commit to master
3. Pull request to Production
  * The pull request will kick off an approval.  Once one other repo writer
    reviews your commit and approves / merges the PR this will kick off the CI
    pipeline.  

# CI Pipeline

Configuration files for the Mozilla SSO-Dashboard. 

