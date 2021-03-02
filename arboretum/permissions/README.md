# Permissions library

The fetchers and checks contained within this `permissions` category folder are
common tests that can be configured and executed for the purpose of generating
compliance reports and notifications using the [auditree-framework][].
See [auditree-framework documentation][] for more details.

These tests are normally executed by a CI/CD system like
[Travis CI](https://travis-ci.com/) as part of another project that uses this
library package as a dependency.

## Usage as a library

See [usage][] for specifics on including this library as a dependency and
how to include the fetchers and checks from this library in your downstream project.

## Fetchers

### Organization Integrity Permissions

* Class: [GithubOrgPermissionFetcher][fetch-org-permissions]
* Purpose: Writes the details of collaborators and repository forks in Github organizations to the evidence locker. This fetcher class is only meant for use with Github or Github Enterprise organizations.
* Behavior: For each Github organization specified, Github collaborator and Github fork evidence files per collaborator type (affiliation) are stored in the locker containing details for the specified repositories in the organization. The default is to retrieve all collaborators and all forks by affiliation from all repositories in each specified Github organization.  TTL is set to 1 day.
* Configuration elements:
  * `org.permissions.org_integrity.orgs`
     * Required
     * List of dictionaries each containing Github organization retrieval configuration.
        * `url`
           * Required
           * String in the form of `"https://github.com/my-org"` or `"https://github.<company>.com/my-org"`.
           * Use to define the Github organization url to use.
        * `repos`
           * Optional
           * List of strings in the form of `["my-repo", "my-other-repo"]`.
           * Defaults to all repositories in the organization.
           * Use if looking to filter permissions evidence to a subset of repositories in the organization otherwise do not include.
        * `collaborator_types`
           * Optional
           * List of strings in the form of `["all", "direct", "outside"]`.
           * Valid list element values are `"all"`, `"direct"`, `"outside"`.
           * Defaults to `["all"]`.
           * Use if looking to override retrieval of all collaborators otherwise do not include.
* Example configuration:

  ```json
  {
    "org": {
      "permissions": {
        "org_integrity": {
          "orgs": [
            {
              "url": "https://github.com/my-org-1"
            },
            {
              "url": "https://github.my-company.com/my-org-2",
              "collaborator_types": ["direct", "outside"],
              "repos": ["repo1", "repo2"]
            }
          ]
        }
      }
    }
  }
  ```

* Required credentials:
  * `github` or `github_enterprise` credentials with [appropriate permissions to the repositories][repository-permissions] are required for this fetcher to successfully retrieve evidence.
     * `username`: The Github user used to run the fetcher.
     * `token`: The Github user access token used to run the fetcher.
  * Example credentials file entry:

     ```ini
     [github]
     username=gh-user-name
     token=gh-access-token
     ```

     or

     ```ini
     [github_enterprise]
     username=ghe-user-name
     token=ghe-access-token
     ```

  * NOTE: These credentials are also needed for basic configuration of the
  Auditree framework. The expectation is that the same credentials are used for all Github interactions.

* Import statement:

  ```python
  from arboretum.permissions.fetchers.github.fetch_org_permissions import GithubOrgPermissionFetcher
  ```

## Checks

### Organization Integrity (Repository Collaborators)

* Class: [OrgCollaboratorsCheck][org-collaborators-check]
* Purpose: Ensure that `direct` collaborators do not exist in the organization repositories.
* Behavior: Collaborators are checked for every repository.
A failure is generated when direct collaborators are found in a repository. This check can be optionally
configured to accept exceptions, a warning instead of a failure is generated for those exceptions when
direct collaborators matching the exceptions are found.
* Evidence depended upon:
    * `direct` collaborators found in organization repositories.
      * `raw/permissions/<gh|gl|bb>_direct_collaborators_<org_url_hash>.json`
      * NOTE: Only gh (Github) is currently supported by this check. Gitlab and Bitbucket support coming soon...
* Configuration elements:
  * `org.permissions.org_integrity.orgs`
     * Required
     * List of dictionaries:
        * `url`
           * Required
           * Organization URL (string).
        * `exceptions`
           * Optional
           * List of dictionaries:
             * `user`
                * Required
                * Github, Gitlab or Bitbucket user id (string). 
                * Use to define the user to be treated as an exception.
                * NOTE: Only Github is currently supported by this check. Gitlab and Bitbucket support coming soon...
             * `repos`
                * Optional
                * List of strings in the form of `["repo_a", "repo_b"]`.
                * Defaults to all repositories in the organization.
                * Use to limit the user exception to specific repositories in the organization.
* Example configuration:

  ```json
  {
    "org": {
      "permissions": {
        "org_integrity": {
          "orgs": [
            {
              "url": "https://github.com/my-org-1",
              "collaborator_types": ["direct"],
              "exceptions": [
                {
                  "user": "userid_1"
                },
                {
                  "user": "userid_2",
                  "repos": ["repo_a", "repo_b"]
                }
              ]
            }
          ]
        }
      }
    }
  }
  ```
* Import statement:
   ```python
   from arboretum.permissions.checks.test_org_collaborators import OrgCollaboratorsCheck
   ```

[auditree-framework]: https://github.com/ComplianceAsCode/auditree-framework
[auditree-framework documentation]: https://complianceascode.github.io/auditree-framework/
[usage]: https://github.com/ComplianceAsCode/auditree-arboretum#usage
[fetch-org-permissions]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/permissions/fetchers/github/fetch_org_permissions.py
[repository-permissions]: https://docs.github.com/en/free-pro-team@latest/github/setting-up-and-managing-organizations-and-teams/repository-permission-levels-for-an-organization
[org-collaborators-check]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/permissions/checks/test_org_collaborators.py