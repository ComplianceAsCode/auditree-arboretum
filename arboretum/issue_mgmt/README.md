# Issue Management library

The fetchers and checks contained within this `issue_mgmt` category folder are
common tests that can be configured and executed for the purpose of generating
compliance reports and notifications using the [auditree-framework][].
See [auditree-framework documentation][] for more details.

These tests are normally executed by a CI/CD system like
[Travis CI](https://travis-ci.com/) as part of another project that uses this
library package as a dependency.

## Usage as a library

See [usage][] for specifics on including this library as a dependency and how
to include the fetchers and checks from this library in your downstream project.

## Fetchers

### Github Issues

* Class: [GithubIssuesFetcher][fetch-gh-issues]
* Purpose: Store Github issues metadata as evidence in the evidence
locker.
* Behavior: For each Github repository specified, an evidence file is stored in
the locker containing the issues for that Github repository based on the provided
search criteria.  TTL is set to 1 day.
* Configuration elements:
   * `org.issue_mgmt.github`
      * Required
      * `is:issue` is applied to all retrieval configuration to limit retrieval
      to Github issues by default.  See the `search` option to expand retrieval
      to pull requests.
      * List of dictionaries each containing issue retrieval configuration.
         * `repo`
            * Required
            * String in the form of `owner/repo`.
            * Use to define the Github repository from where issues will be
            extracted.
         * `host`
            * Optional
            * String in the form of `https://github.my_org.com`.
            * Defaults to `https://github.com` (public Github)
            * Use if the repo is a Github Enterprise repo otherwise do not include.
         * `states`
            * Optional
            * List of string in the form of `["open", "closed"]`.
            * Valid list element values are `"open"` and `"closed"`.
            * Values are applied as `OR` logic to the search for issues.
            * Defaults to `["open"]`.
            * Use if looking to retrieve closed or both open and closed issues
            otherwise do not include.
         * `labels`
            * Optional
            * Dictionary of string key/value pairs
               * Valid keys: `"equals"`, `"contains"`, `"startswith"`, and
               `"endswith"`.
               * Valid values: List of strings
               * Each pair is applied as `OR` logic to the search for issues.
            * Defaults to all labels.
            * Use if looking to limit issues to issues containing specific labels
            other do not include.
         * `search`
            * Optional
            * String in the form of a [Github search query string][gh-issues-search].
               * Use of `search` overrides all other configuration.
               * `is:issue` is automatically prepended to every search query
               provided.
            * Use if looking for finer granularity in your Github issue search
            criteria otherwise do not include.

* Example configuration:

   ```json
   {
     "org": {
       "issue_mgmt": {
         "github": [
           {
             "repo": "foo-owner/foo-repo",
             "host": "https://github.foo.com",
             "states": ["open", "closed"],
             "labels": {
               "equals": ["label-one", "label-two"],
               "contains": ["foo"],
               "startswith": ["bar"],
               "endswith": ["baz"]
             }
           },
           {
             "repo": "bar-owner/bar-repo",
             "search": "is:open is:closed in:title 'words in my title'"
           }
         ]
       }
     }
   }
   ```

* Required credentials:
   * `github` or `github_enterprise` credentials with read permissions to the
   repository are required for this fetcher to successfully retrieve evidence.
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
   Auditree framework.  The expectation is that the same credentials are used
   for all Github interactions.

* Import statement:

   ```python
   from arboretum.issue_mgmt.fetchers.fetch_github_issues import GithubIssuesFetcher
   ```

### Zenhub Workspaces

* Class: [ZenhubWorkspacesFetcher][fetch-zh-workspaces]
* Purpose: Store Zenhub workspaces metadata as evidence in the evidence
locker.
* Behavior: For each Github repository specified, an evidence file is stored in
the locker containing the Zenhub workspace boards specified.  TTL is set to 1 day.
* Configuration elements:
   * `org.issue_mgmt.zenhub`
      * Required
      * List of dictionaries each containing workspace retrieval configuration.
         * `github_repo`
            * Required
            * String in the form of `owner/repo`.
            * Use to define the target Github repository for which workspaces
            are retrieved.
         * `github_host`
            * Optional
            * String in the form of `https://github.my_org.com`.
            * Defaults to `https://github.com` (public Github)
            * Use if the repo is a Github Enterprise repo otherwise do not include.
         * `api_root`
            * Optional
            * String in the form of `https://zenhub.my_org.com`.
            * Defaults to `https://api.zenhub.com/` (public Zenhub API)
            * Use if the target is Zenhub Enterprise otherwise do not include.
         * `workspaces`
            * Optional
            * List of strings
            * Valid values in the list include valid Zenhub workspace names for
            the given Github repository.
            * Use if looking to limit workspace retrieval to a subset of workspaces
            otherwise do not include.

* Example configuration:

   ```json
   {
     "org": {
       "issue_mgmt": {
         "zenhub": [
           {
             "github_repo": "foo-owner/foo-repo",
             "github_host": "https://github.foo.com",
             "api_root": "https://zenhub.foo.com",
             "workspaces": ["My super cool foo workspace"]
           },
           {
             "github_repo": "bar-owner/bar-repo",
             "workspaces": ["My super cool bar workspace", "Some other workspace"]
           }
         ]
       }
     }
   }
   ```

* Required credentials:
   * `github` or `github_enterprise` credentials with read permissions to the
   repository are required for this fetcher to successfully retrieve evidence.
      * `username`: The Github user used to run the fetcher.
      * `token`: The Github user access token used to run the fetcher.
   * `zenhub` or `zenhub_enterprise` credentials with read permissions to the
   Zenhub API are required for this fetcher to successfully retrieve evidence.
   * Example credentials file entry:

      ```ini
      [github]
      username=gh-user-name
      token=gh-access-token

      [zenhub]
      token=zh-access-token
      ```

      or

      ```ini
      [github_enterprise]
      username=ghe-user-name
      token=ghe-access-token

      [zenhub_enterprise]
      token=zhe-access-token
      ```

   * NOTE: The Github credentials are also needed for basic configuration of the
   Auditree framework.  The expectation is that the same credentials are used
   for all Github interactions.
   * NOTE: See [Zenhub API Authentication][zh-auth] for details on generating
   Zenhub API tokens.

* Import statement:

   ```python
   from arboretum.issue_mgmt.fetchers.fetch_zenhub_workspaces import ZenhubWorkspacesFetcher
   ```

## Checks

Checks coming soon...

[auditree-framework]: https://github.com/ComplianceAsCode/auditree-framework
[auditree-framework documentation]: https://complianceascode.github.io/auditree-framework/
[usage]: https://github.com/ComplianceAsCode/auditree-arboretum#usage
[fetch-gh-issues]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/issue_mgmt/fetchers/fetch_github_issues.py
[fetch-zh-workspaces]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/issue_mgmt/fetchers/fetch_zenhub_workspaces.py
[gh-issues-search]: https://docs.github.com/en/free-pro-team@latest/github/searching-for-information-on-github/searching-issues-and-pull-requests
[zh-auth]: https://github.com/ZenHubIO/API#authentication
