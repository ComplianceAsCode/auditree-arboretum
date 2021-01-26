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

### Organization Integrity (Repository Collaborators)

* Class: [GithubOrgCollaboratorsFetcher][gh-org-fetcher]
* Purpose: Writes the details of collaborators in Github organizations to the evidence locker. This fetcher class is only meant for use with Github or Github Enterprise organizations.
* Behavior: For each Github organization specified, an evidence file per collaborator type (affiliation) is stored in
the locker containing collaborator details for the specified repositories in the organization. The default is to
retrieve all collaborators by affiliation from all repositories in each specified Github organization.  TTL is set to 1
day.
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
           * Use if looking to filter collaborator evidence to a subset of repositories in the organization otherwise do not include.
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
  from arboretum.permissions.fetchers.github.fetch_org_collaborators import GithubOrgCollaboratorsFetcher
  ```

## Checks

### Organization Integrity (Repository Collaborators)

* Class: [OrgCollaboratorsCheck][org-check]

* Purpose: Ensure that `direct` collaborators do not exist in the repositories of the organizations

* Behavior: Failures are issued when direct collaborators are found in the evidences collected by a valid fetcher. Supported fetchers:
    * [GithubOrgCollaboratorsFetcher][gh-org-fetcher] fetcher

* Evidence depended upon:
    * The organization direct collaborators evidence for each organization/repositories specified in the fetcher's configuration
if `direct` is included as a collaborators type in the configuration:
      * `raw/permissions/<service>_direct_collaborators_<org_url_hash>.json`


* Import statement:
  `from arboretum.permissions.checks.test_org_direct_collaborators import OrgCollaboratorsCheck`

[auditree-framework]: https://github.com/ComplianceAsCode/auditree-framework
[auditree-framework documentation]: https://complianceascode.github.io/auditree-framework/
[usage]: https://github.com/ComplianceAsCode/auditree-arboretum#usage
[gh-org-fetcher]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/permissions/fetchers/github/fetch_org_collaborators.py
[repository-permissions]: https://docs.github.com/en/free-pro-team@latest/github/setting-up-and-managing-organizations-and-teams/repository-permission-levels-for-an-organization
[org-check]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/permissions/checks/test_org_direct_collaborators.py
