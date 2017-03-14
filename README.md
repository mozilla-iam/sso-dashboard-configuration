# sso-dashboard-configuration
Configuration files for the Mozilla SSO-Dashboard.

# How it works...

The apps.yml controls app visibility in the dashboard based on group membership
or lists of users.  

Groups are simple _name of group_.  Users are identified by their mozilla
e-mail.

# Git workflow

In order to publish a change you must:

1. Clone the repository
2. Commit to master
3. Pull request to Production
  * The pull request will kick off an approval.  Once one other repo writer
    reviews your commit and approves / merges the PR this will kick off the CI
    pipeline.  

# CI Pipeline
