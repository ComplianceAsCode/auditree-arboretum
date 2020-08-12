# Auditree library

The fetchers and checks contained within this `auditree` category folder are
common tests that can be configured and executed for the purpose of generating
compliance reports and notifications using the [auditree-framework][].  They
validate the configuration and ensure smooth execution of an auditree instance.
See [auditree-framework documentation](https://complianceascode.github.io/auditree-framework/)
for more details.

These tests are normally executed by a CI/CD system like
[Travis CI](https://travis-ci.com/) as part of another project that uses this
library package as a dependency.

## Usage as a library

See [usage][usage] for specifics on including this library as a dependency and
how to include the fetchers and checks from this library in your downstream project.

## Fetchers

### Abandoned Evidence

* Class: [AbandonedEvidenceFetcher][fetch-abandoned-evidence]
* Purpose: Writes evidence that has been identified as abandoned to the evidence
locker.
* Behavior: Stores abandoned evidence and abandoned evidence exceptions to the
evidence locker.  If the optional `threshold` configuration setting is applied
then abandoned evidence is identified as evidence that has not been updated in
over that `threshold` value otherwise the default is 30 days.  TTL is set to 1 day.
* Configuration elements:
   * `org.auditree.abandoned_evidence.threshold`
      * Optional
      * Integer
      * Provide value in seconds
      * Use if looking to override the default of 30 days.  Otherwise do not include.
   * `org.auditree.abandoned_evidence.exceptions`
      * Optional
      * Dictionary where the key/value pairs are the path to the evidence (key)
      and the reason for excluding it from the abandoned evidence list (value).
      * Key/Value: String/String
      * Use if looking to exclude evidence files from being deemed abandoned and
      included as failures.  All "exceptions" will still appear on the report and
      will be treated as warnings rather than failures.
* Example (optional) configuration:

   ```json
   {
     "org": {
       "auditree": {
         "abandoned_evidence": {
           "threshold": 1234567,
           "exceptions": {
             "raw/path/to-evidence.json": "This is a good reason",
             "raw/path/to-evidence-2.json": "This is also a good reason"
           }
         }
       }
     }
   }
   ```

* Import statement:

   ```python
   from arboretum.auditree.fetchers.fetch_abandoned_evidence import AbandonedEvidenceFetcher
   ```

### Compliance Configuration

* Class: [ComplianceConfigFetcher][fetch-compliance-config]
* Purpose: Writes the current configuration stored in the ComplianceConfig object
to the evidence locker.
* Behavior: Stores the configuration used to execute the compliance fetchers to
the evidence locker and sets a time to live (TTL) to 2 hours.  This fetcher
ignores TTL and will refresh the configuration evidence on every execution of
the fetchers.
* Import statement:

   ```python
   from arboretum.auditree.fetchers.fetch_compliance_config import ComplianceConfigFetcher
   ```

### Repository Integrity (Metadata)

* Class: [GithubRepoMetaDataFetcher][fetch-repo-metadata]
* Purpose: Writes Github repository metadata details evidence to the evidence
locker.  This fetcher class is only meant for use with Github or Github
Enterprise repositories.
* Behavior: For each Github repository specified, an evidence file is stored in
the locker containing that repository's metadata details.  If no repositories
are specified the fetcher defaults to retrieving the evidence locker repository
metadata detail.  TTL is set to 1 day.
* Configuration elements:
   * `org.auditree.repo_integrity.repos`
      * Optional
      * List of Github repository URLs (string).
      * Use if looking to specify multiple repos or to override the evidence
      locker repo default.  Otherwise do not include.
* Example (optional) configuration:

   ```json
   {
     "org": {
       "auditree": {
         "repo_integrity": {
           "repos": [
             "https://github.com/org-foo/repo-foo",
             "https://github.com/org-bar/repo-bar"
           ]
         }
       }
     }
   }
   ```

* Required credentials:
   * `github` or `github_enterprise` credentials with admin permissions to the
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
   from arboretum.auditree.fetchers.github.fetch_repo_metadata import GithubRepoMetaDataFetcher
   ```

### Repository Integrity (Recent Commits)

* Class: [GithubRepoCommitsFetcher][fetch-recent-commits]
* Purpose: Writes the most recent Github repository branch commit details
to the evidence locker.  This fetcher class is only meant for use with Github
or Github Enterprise repositories.
* Behavior: For each Github repository and branch specified, an evidence file
is stored in the locker containing that repository branch's most recent (last 2
days) commit details.  If no repositories are specified the fetcher defaults to
retrieving the evidence locker `master` branch commit detail.  TTL is set to 1
day.
* Configuration elements:
   * `org.auditree.repo_integrity.branches`
      * Optional
      * Dictionary:
         * Key: Github repository URL (string)
         * Value: List of branches (string) for that repository.
      * Use if looking to specify multiple repos/branches or to override the
      evidence locker repo and `master` branch default.  Otherwise do not include.
* Example (optional) configuration:

   ```json
   {
     "org": {
       "auditree": {
         "repo_integrity": {
           "branches": {
             "https://github.com/org-foo/repo-foo": ["main", "develop"],
             "https://github.com/org-bar/repo-bar": ["main"]
           }
         }
       }
     }
   }
   ```

* Required credentials:
   * `github` or `github_enterprise` credentials with admin permissions to the
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
   from arboretum.auditree.fetchers.github.fetch_recent_commits import GithubRepoCommitsFetcher
   ```

### Repository Integrity (Branch Protection)

* Class: [GithubRepoBranchProtectionFetcher][fetch-branch-protection]
* Purpose: Writes the Github repository branch protection details to the
evidence locker.  This fetcher class is only meant for use with Github or
Github Enterprise repositories.
* Behavior: For each Github repository and branch specified, an evidence file
is stored in the locker containing that repository branch's branch protection
details.  If no repositories are specified the fetcher defaults to retrieving
the evidence locker `master` branch branch protection detail.  TTL is set to 1
day.
* Configuration elements:
   * `org.auditree.repo_integrity.branches`
      * Optional
      * Dictionary:
         * Key: Github repository URL (string)
         * Value: List of branches (string) for that repository.
      * Use if looking to specify multiple repos/branches or to override the
      evidence locker repo and `master` branch default.  Otherwise do not include.
* Example (optional) configuration:

   ```json
   {
     "org": {
       "auditree": {
         "repo_integrity": {
           "branches": {
             "https://github.com/org-foo/repo-foo": ["main", "develop"],
             "https://github.com/org-bar/repo-bar": ["main"]
           }
         }
       }
     }
   }
   ```

* Required credentials:
   * `github` or `github_enterprise` credentials with admin permissions to the
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
   from arboretum.auditree.fetchers.github.fetch_branch_protection import GithubRepoBranchProtectionFetcher
   ```

### Python Packages

* Class: [PythonPackageFetcher][fetch-python-packages]
* Purpose: Writes the current Python package dependency list to evidence.
* Behavior: Stores the current Python package dependency list as evidence and
the latest release information for `auditree-arboretum`, `auditree-framework`
and `auditree-harvest` are also retrieved and stored as evidence.  The time to
live (TTL) is set to 1 day for all evidences.
* Import statement:

   ```python
   from arboretum.auditree.fetchers.fetch_python_packages import PythonPackageFetcher
   ```

## Checks

### Abandoned Evidence

* Class: [AbandonedEvidenceCheck][check-abandoned-evidence]
* Purpose: For every piece of evidence that has not been updated for longer than
the time to live plus the specified threshold a failure is generated and reported.
* Behavior: Performs a check that compares abandoned evidence identified on a given
check execution with the last time new abandoned evidence was found and reports
on newly found abandoned evidence and possible exceptions.  If no "abandoned evidence"
evidence is contained within the locker then this check traverses the evidence
locker repository and identifies evidence that has not been updated for a specific
period of time and reports on abandoned evidence found for the current check
execution.  The default threshold is 30 days beyond the time to live (TTL) setting.
* Evidence depended upon:
   * Abandoned evidence and exceptions
      * `raw/auditree/abandoned_evidence.json`
      * Gathered by the `auditree` provider [AbandonedEvidenceFetcher][fetch-abandoned-evidence]
   * If the [AbandonedEvidenceFetcher][fetch-abandoned-evidence] is not used to
   store "abandoned evidence" evidence in the locker then the tooling performs
   a sweep of the evidence locker metadata to assess evidence that has not been
   updated in the timeframe specified.
* Configuration elements:
   * `org.auditree.abandoned_evidence.threshold`
      * Optional
      * Integer
      * Provide value in seconds
      * Use if looking to override the default of 30 days.  Otherwise do not include.
   * `org.auditree.abandoned_evidence.exceptions`
      * Optional
      * Dictionary where the key/value pairs are the path to the evidence (key)
      and the reason for excluding it from the abandoned evidence list (value).
      * Key/Value: String/String
      * Use if looking to exclude evidence files from being deemed abandoned
      and included as failures.  All "exceptions" will still appear on the
      report and will be treated as warnings rather than failures.
   * `org.auditree.abandoned_evidence.ignore_history`
      * Optional
      * Boolean
      * Set to `true`
      * Use if collecting `raw/auditree/abandoned_evidence.json` in the evidence
      locker but intend to run the check without referencing the evidence history
      (more rigid alerts).  Otherwise do not include.
* Example (optional) configuration:

   ```json
   {
     "org": {
       "auditree": {
         "abandoned_evidence": {
           "threshold": 1234567,
           "exceptions": {
             "raw/path/to-evidence.json": "This is a good reason",
             "raw/path/to-evidence-2.json": "This is also a good reason"
           },
           "ignore_history": true
         }
       }
     }
   }
   ```

* Import statement:

   ```python
   from arboretum.auditree.checks.test_abandoned_evidence import AbandonedEvidenceCheck
   ```

### Compliance Configuration

* Class: [ComplianceConfigCheck][check-compliance-config]
* Purpose: Compare the configuration captured as evidence with the current
configuration in the ComplianceConfig object being used to execute the checks.
* Behavior: For every difference found between the evidence and the current
configuration a failure is generated and reported on.
* Evidence depended upon:
   * Compliance tooling configuration settings
      * `raw/auditree/compliance_config.json`
      * Gathered by the `auditree` provider [ComplianceConfigFetcher][fetch-compliance-config]
* Import statement:

   ```python
   from arboretum.auditree.checks.test_compliance_config import ComplianceConfigCheck
   ```

### Python Packages

* Class: [PythonPackageCheck][check-python-packages]
* Purpose: Compare the most recent Python package evidence with the evidence
from the most recent historical version of that evidence found in the locker and
checks that the `auditree-arboretum`, `auditree-framework` and `auditree-harvest`
packages are at their most current release level.
* Behavior: For every difference found between the two versions of evidence a
warning is generated and reported on.  Warnings are also generated when the
`auditree-arboretum`, `auditree-framework`, or `auditree-harvest` packages being
used are not at the current release version.
* Evidence depended upon:
   * The executing environment's Python package list
      * `raw/auditree/python_packages.json`
      * `raw/auditree/auditree_arboretum_releases.xml`
      * `raw/auditree/auditree_framework_releases.xml`
      * `raw/auditree/auditree_harvest_releases.xml`
      * Gathered by the `technology.auditree` [PythonPackageFetcher][fetch-python-packages]
* Import statement:

   ```python
   from arboretum.auditree.checks.test_python_packages import PythonPackageCheck
   ```

[usage]: https://github.com/ComplianceAsCode/auditree-arboretum#usage
[fetch-abandoned-evidence]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/auditree/fetchers/fetch_abandoned_evidence.py
[fetch-compliance-config]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/auditree/fetchers/fetch_compliance_config.py
[fetch-python-packages]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/auditree/fetchers/fetch_python_packages.py
[fetch-repo-metadata]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/auditree/fetchers/github/fetch_repo_metadata.py
[fetch-recent-commits]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/auditree/fetchers/github/fetch_recent_commits.py
[fetch-branch-protection]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/auditree/fetchers/github/fetch_branch_protection.py
[check-abandoned-evidence]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/auditree/checks/test_abandoned_evidence.py
[check-compliance-config]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/auditree/checks/test_compliance_config.py
[check-python-packages]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/auditree/checks/test_python_packages.py
