# Auditree library

The fetchers and checks contained within this `auditree` category folder are
common tests that can be configured and executed for the purpose of generating
compliance reports and notifications using the [auditree-framework][].  They
validate the configuration and ensure smooth execution of an auditree instance.
See [auditree-framework documentation][] for more details.

These tests are normally executed by a CI/CD system like
[Travis CI](https://travis-ci.com/) as part of another project that uses this
library package as a dependency.

## Usage as a library

See [usage][] for specifics on including this library as a dependency and how
to include the fetchers and checks from this library in your downstream project.

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
   from arboretum.auditree.fetchers.github.fetch_repo_metadata import GithubRepoMetaDataFetcher
   ```

### Repository Integrity (Recent Commits)

* Class: [GithubRepoCommitsFetcher][fetch-recent-commits]
* Purpose: Writes the most recent Github repository branch commit details
to the evidence locker.  This fetcher class is only meant for use with Github
or Github Enterprise repositories.
* Behavior: For each Github repository and branch specified, an evidence file
is stored in the locker containing that repository branch's most recent (since
the last time the evidence was fetched) commit details.  If no repositories
are specified the fetcher defaults to retrieving the evidence locker `master`
branch commit detail.  TTL is set to 2 days for the evidence locker and 1 day
for all other repositories/branches.
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
   from arboretum.auditree.fetchers.github.fetch_recent_commits import GithubRepoCommitsFetcher
   ```

### Repository Integrity (Recent File Path Commits)

* Class: [GithubFilePathCommitsFetcher][fetch-filepath-commits]
* Purpose: Writes the most recent Github repository branch file path commit
details to the evidence locker.  This fetcher class is only meant for use with
Github or Github Enterprise repositories.
* Behavior: For each Github repository, branch and file path specified, an
evidence file is stored in the locker containing that repository branch file
path's most recent (since the last time the evidence was collected) commit
details.  A file path can be a relative path to a file or a folder within the
repository.  TTL is set to 1 day.
* Configuration elements:
   * `org.auditree.repo_integrity.filepaths`
      * Required
      * Dictionary:
         * Key: Github repository URL (string)
         * Value: Dictionary of branches and file paths within the branch.
            * Key: Branch name (string)
            * Value: List of file paths (string) for that repository/branch.
* Example (required) configuration:

   ```json
   {
     "org": {
       "auditree": {
         "repo_integrity": {
           "filepaths": {
             "https://github.com/org-foo/repo-foo": {
               "main": ["foo", "bar/baz.json"],
               "develop": ["README.md"]
             },
             "https://github.com/org-bar/repo-bar": {
               "main": ["README.md", "foo/bar/baz.py"]
             }
           }
         }
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
   from arboretum.auditree.fetchers.github.fetch_filepath_commits import GithubFilePathCommitsFetcher
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
      * Gathered by the `auditree` [AbandonedEvidenceFetcher][fetch-abandoned-evidence]
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

### Empty Evidence

* Class: [EmptyEvidenceCheck][check-empty-evidence]
* Purpose: For every piece of evidence that has no content a failure is generated
and reported.
* Behavior: Performs a check that validates the content of evidence is not empty.
Empty evidence content is based on an evidence object's `is_empty` property which
can vary across evidences.  But the default `is_empty` criteria is as follows:
   * Content is all whitespace.
   * In the case of JSON, content is an empty dictionary or list (`{}`, `[]`).
* Evidence depended upon:
   * This check does not depend on any evidence specifically.  It acts on **all**
   evidence contained within an evidence locker.
* Configuration elements:
   * `org.auditree.empty_evidence.exceptions`
      * Optional
      * List where the list elements are the relative evidence locker paths to
      evidence files.
      * Use if looking to exclude specific evidence files from being flagged as
      failures.  All "exceptions" will still appear on the report and will be
      treated as warnings rather than failures.
* Example (optional) configuration:

   ```json
   {
     "org": {
       "auditree": {
         "empty_evidence": {
           "exceptions": [
             "raw/path/to-evidence.json",
             "raw/path/to-evidence-2.json"
           ]
         }
       }
     }
   }
   ```

* Import statement:

   ```python
   from arboretum.auditree.checks.test_empty_evidence import EmptyEvidenceCheck
   ```

### Evidence Locker Large Files

* Class: [LargeFilesCheck][check-large-files]
* Purpose: Remote hosting services have file size constraints that if violated
will cause a remote push of the locker to be rejected.  This check identifies
"large" sized files so they can be dealt with prior to reaching the remote
hosting service file size constraint.
* Behavior: Performs a check that flags all files in the evidence locker
(evidence and non-evidence) that exceed a large file threshold setting as
failures and flags all files within 20% of the threshold as warnings.  The
large file threshold defaults to 50MB.
* Evidence depended upon:
   * This check does not depend on any evidence specifically.  It acts on **all**
   files contained within an evidence locker.
* Configuration elements:
   * `locker.large_file_threshold`
      * Optional
      * File size threshold in bytes as an integer
      * Use if looking to override the default of 50MB.  Otherwise do not include.
      * NOTE: This is the same [evidence locker][] configuration setting is used by
      the framework to produce large file execution log INFO messages.
* Example (optional) configuration:

   ```json
   {
     "locker": {
       "large_file_threshold": 50000000
     }
   }
   ```

* Import statement:

   ```python
   from arboretum.auditree.checks.test_locker_large_files import LargeFilesCheck
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
      * Gathered by the `auditree` [ComplianceConfigFetcher][fetch-compliance-config]
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
   * The executing environment's Python package list and PyPI release evidence
   for arboretum, the framework, and harvest.
      * `raw/auditree/python_packages.json`
      * `raw/auditree/auditree_arboretum_releases.xml`
      * `raw/auditree/auditree_framework_releases.xml`
      * `raw/auditree/auditree_harvest_releases.xml`
      * Gathered by the `auditree` [PythonPackageFetcher][fetch-python-packages]
* Import statement:

   ```python
   from arboretum.auditree.checks.test_python_packages import PythonPackageCheck
   ```

### Evidence Locker Repository Integrity

* Class: [LockerRepoIntegrityCheck][check-locker-integrity]
* Purpose: Ensure that evidence locker(s) have not been tampered with.
* Behavior: For every evidence locker specified, a comparison between the current
and most recent evidence locker repository metadata is performed.  If changes are
found a failure is generated by the check.  A failure is also generated if
branch protection is disabled for repository administrators on branches specified.
Finally, a warning is generated if the evidence locker size has shrunk when comparing
the current and most recent evidence locker repository metadata.  This check can
be optionally configured to check multiple evidence lockers and branches.  If
no configuration is provided the check defaults to the repository configuration,
if provided.  Otherwise, the check defaults to running against the current evidence
locker URL.
* Evidence depended upon:
   * Evidence locker(s) metadata and branch protection evidence.
      * `raw/auditree/<gh|gl|bb>_<org>_<repo>_repo_metadata.json`
      * `raw/auditree/<gh|gl|bb>_<org>_<repo>_<branch>_branch_protection.json`
      * Gathered by the `auditree` [GithubRepoMetaDataFetcher][fetch-repo-metadata]
      and the `auditree` [GithubRepoBranchProtectionFetcher][fetch-branch-protection]
      * NOTE:  Only `gh` (Github) is currently supported by this check.  Gitlab
      and Bitbucket support coming soon...
* Configuration elements:
   * `org.auditree.locker_integrity.repos`
      * Optional
      * List of repository URLs (string).
      * Use if looking to specify multiple repos or to override either the
      `repo_integrity` config or the the evidence locker repo default.  Otherwise
      do not include.
   * `org.auditree.locker_integrity.branches`
      * Optional
      * Dictionary:
         * Key: Repository URL (string)
         * Value: List of branches (string) for that repository.
      * Use if looking to specify multiple repos/branches or to override either the
      `repo_integrity` config or the the evidence locker repo and `master` branch
      default.  Otherwise do not include.
* Example (optional) configuration:

   ```json
   {
     "org": {
       "auditree": {
         "locker_integrity": {
           "repos": [
             "https://github.com/org-foo/repo-foo",
             "https://github.com/org-bar/repo-bar"
           ],
           "branches": {
             "https://github.com/org-foo/repo-foo": ["main", "develop"],
             "https://github.com/org-bar/repo-bar": ["main"]
           }
         }
       }
     }
   }
   ```

* Import statement:

   ```python
   from arboretum.auditree.checks.test_locker_repo_integrity import LockerRepoIntegrityCheck
   ```

### Evidence Locker Commit Integrity

* Class: [LockerCommitIntegrityCheck][check-locker-commit-integrity]
* Purpose: Ensure that evidence locker(s) commits are signed.
* Behavior: For every evidence locker and branch specified, commits are checked
for a verified signature and branch protection is also checked to ensure that
commit signatures are required.  Failures are generated for each violation found.
This check can be optionally configured to check multiple evidence lockers and
branches.  If no configuration is provided the check defaults to the repository
configuration, if provided.  Otherwise, the check defaults to running against
the current evidence locker URL.
* Evidence depended upon:
   * Evidence locker(s) recent commits and branch protection evidence.
      * `raw/auditree/<gh|gl|bb>_<org>_<repo>_<branch>_recent_commits.json`
      * `raw/auditree/<gh|gl|bb>_<org>_<repo>_<branch>_branch_protection.json`
      * Gathered by the `auditree` [GithubRepoCommitsFetcher][fetch-recent-commits]
      and the `auditree` [GithubRepoBranchProtectionFetcher][fetch-branch-protection]
      * NOTE:  Only `gh` (Github) is currently supported by this check.  Gitlab
      and Bitbucket support coming soon...
* Configuration elements:
   * `org.auditree.locker_integrity.branches`
      * Optional
      * Dictionary:
         * Key: Repository URL (string)
         * Value: List of branches (string) for that repository.
      * Use if looking to specify multiple repos/branches or to override either the
      `repo_integrity` config or the the evidence locker repo and `master` branch
      default.  Otherwise do not include.
* Example (optional) configuration:

   ```json
   {
     "org": {
       "auditree": {
         "locker_integrity": {
           "branches": {
             "https://github.com/org-foo/repo-foo": ["main", "develop"],
             "https://github.com/org-bar/repo-bar": ["main"]
           }
         }
       }
     }
   }
   ```

* Import statement:

   ```python
   from arboretum.auditree.checks.test_locker_commit_integrity import LockerCommitIntegrityCheck
   ```

### New Commits - Repository/Branch

* Class: [RepoBranchNewCommitsCheck][check-repo-branch-new-commits]
* Purpose: Ensure that stable repository branches are not receiving any new commits.
* Behavior: A warning is issued for each repository and branch specified, when
commits are found since the last time the check ran.  The expectation
is that stable/frozen repositories will not be getting new commits.  This check
validates that.
* Evidence depended upon:
   * Recent commits made to repository branches.
      * `raw/auditree/<gh|gl|bb>_<org>_<repo>_<branch>_recent_commits.json`
      * Gathered by the `auditree` [GithubRepoCommitsFetcher][fetch-recent-commits]
      * NOTE:  Only `gh` (Github) is currently supported by this check.  Gitlab
      and Bitbucket support coming soon...
* Configuration elements:
   * `org.auditree.repo_integrity.branches`
      * Required
      * Dictionary:
         * Key: Repository URL (string)
         * Value: List of branches (string) for that repository.
      * NOTE: If the current locker repo/branch for the execution environment
      is included as part of this configuration element, it will be ignored by
      the check.
* Example (required) configuration:

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

* Import statement:

   ```python
   from arboretum.auditree.checks.test_repo_branch_commits import RepoBranchNewCommitsCheck
   ```

### New Commits - Repository/Branch/Filepath

* Class: [FilepathNewCommitsCheck][check-filepath-new-commits]
* Purpose: Ensure that stable file folders and files in repository branches are
not receiving any new commits.
* Behavior: A warning is issued for each repository, branch and file path
specified, when commits are found since the last time the check ran.  The
expectation is that stable/frozen repository branch folders/files will not be
getting new commits.  This check validates that.
* Evidence depended upon:
   * Recent commits made to file folders or files in repository branches.
      * `raw/auditree/<gh|gl|bb>_<org>_<repo>_<branch>_<filepath>_recent_commits.json`
      * Gathered by the `auditree`
      [GithubFilePathCommitsFetcher][fetch-filepath-commits]
      * NOTE:  Only `gh` (Github) is currently supported by this check.  Gitlab
      and Bitbucket support coming soon...
* Configuration elements:
   * `org.auditree.repo_integrity.filepaths`
      * Required
      * Dictionary:
         * Key: Repository URL (string)
         * Value: Dictionary of branches and file paths within the branch.
            * Key: Branch name (string)
            * Value: List of file paths (string) for that repository/branch.
* Example (required) configuration:

   ```json
   {
     "org": {
       "auditree": {
         "repo_integrity": {
           "filepaths": {
             "https://github.com/org-foo/repo-foo": {
               "main": ["foo", "bar/baz.json"],
               "develop": ["README.md"]
             },
             "https://github.com/org-bar/repo-bar": {
               "main": ["README.md", "foo/bar/baz.py"]
             }
           }
         }
       }
     }
   }
   ```

* Import statement:

   ```python
   from arboretum.auditree.checks.test_filepath_commits import FilepathNewCommitsCheck
   ```

[auditree-framework]: https://github.com/ComplianceAsCode/auditree-framework
[auditree-framework documentation]: https://complianceascode.github.io/auditree-framework/
[usage]: https://github.com/ComplianceAsCode/auditree-arboretum#usage
[evidence locker]: https://complianceascode.github.io/auditree-framework/design-principles.html#evidence-locker
[fetch-abandoned-evidence]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/auditree/fetchers/fetch_abandoned_evidence.py
[fetch-compliance-config]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/auditree/fetchers/fetch_compliance_config.py
[fetch-python-packages]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/auditree/fetchers/fetch_python_packages.py
[fetch-repo-metadata]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/auditree/fetchers/github/fetch_repo_metadata.py
[fetch-recent-commits]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/auditree/fetchers/github/fetch_recent_commits.py
[fetch-filepath-commits]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/auditree/fetchers/github/fetch_filepath_commits.py
[fetch-branch-protection]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/auditree/fetchers/github/fetch_branch_protection.py
[check-abandoned-evidence]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/auditree/checks/test_abandoned_evidence.py
[check-empty-evidence]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/auditree/checks/test_empty_evidence.py
[check-large-files]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/auditree/checks/test_locker_large_files.py
[check-compliance-config]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/auditree/checks/test_compliance_config.py
[check-python-packages]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/auditree/checks/test_python_packages.py
[check-locker-integrity]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/auditree/checks/test_locker_repo_integrity.py
[check-locker-commit-integrity]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/auditree/checks/test_locker_commit_integrity.py
[check-repo-branch-new-commits]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/auditree/checks/test_repo_branch_commits.py
[check-filepath-new-commits]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/auditree/checks/test_filepath_commits.py
