[![OS Compatibility][platform-badge]](#prerequisites)
[![Python Compatibility][python-badge]][python-dl]
[![pre-commit][pre-commit-badge]][pre-commit]
[![Code validation](https://github.com/ComplianceAsCode/auditree-arboretum/workflows/format%20%7C%20lint%20%7C%20test/badge.svg)][lint-test]
[![Upload Python Package](https://github.com/ComplianceAsCode/auditree-arboretum/workflows/PyPI%20upload/badge.svg)][pypi-upload]

# auditree-arboretum

The Auditree common fetchers, checks and [harvest][] reports library.

## Introduction

Auditree Arboretum is a Python library of common compliance fetchers, checks &amp; harvest
reports built upon the [Auditree compliance automation framework][auditree-framework].

## Repo content

### Functionality categorization

Arboretum fetchers, checks, and Harvest reports are organized into functional
grouping categories.  The following categories have either been contributed to
or will be contributed to in the near future.  We anticipate that this list will
grow as arboretum matures.

- [Ansible](https://github.com/ComplianceAsCode/auditree-arboretum/tree/main/arboretum/ansible)
- [Auditree](https://github.com/ComplianceAsCode/auditree-arboretum/tree/main/arboretum/auditree)
- [Chef](https://github.com/ComplianceAsCode/auditree-arboretum/tree/main/arboretum/chef)
- [IBM Cloud](https://github.com/ComplianceAsCode/auditree-arboretum/tree/main/arboretum/ibm_cloud)
- [Kubernetes](https://github.com/ComplianceAsCode/auditree-arboretum/tree/main/arboretum/kubernetes)
- [Object Storage](https://github.com/ComplianceAsCode/auditree-arboretum/tree/main/arboretum/object_storage)
- [Pager Duty](https://github.com/ComplianceAsCode/auditree-arboretum/tree/main/arboretum/pager_duty)
- [Splunk](https://github.com/ComplianceAsCode/auditree-arboretum/tree/main/arboretum/splunk)

### Fetchers

Please read the framework documentation for [fetcher design principles][] before
contributing a fetcher.

Fetchers must apply no logic to the data they retrieve. They must write unadulterated
(modulo sorting & de-duplication) into the `/raw` area of the locker via the
framework-provided decorators or context managers.

Fetchers must be atomic - retrieving and creating the data they are responsible
for. Fetcher execution order is not guaranteed and so you must not assume that
evidence already exists and is current in the locker.  Use
[evidence dependency chaining][] if a fetcher depends on evidence gathered by another
fetcher in order to gather its intended evidence.

Fetchers should be as fast as the API call allows. If a call is long running it
should be separated into a dedicated evidence providing tool, which places data
where a fetcher can retrieve it easily & quickly.

### Checks

Please read the framework documentation for [check design principles][] before
contributing a check.

Checks should only use evidence from the evidence locker to perform check operations.
Also, checks **should not** write or change evidence from the evidence locker.  That
is the job of a fetcher.

[Jinja][] is used to produce reports from checks.  As such each check class must have
at least one associated report template in order to produce a check report.  In keeping
with the "DevSecOps" theme, check reports are meant to provide details on violations
identified by checks.  These violations are in the form of failures and warnings.
**They aren't meant to be used to format fetched raw evidence into a readable report.**
[Harvest][harvest] reports should be used to satisfy that need.

### Harvest Reports

Harvest reports are hosted with the fetchers/checks that collect the evidence for
the reports process. Within `auditree-arboretum` this means the harvest report code
lives in `reports` folders throughout this repository. For more details check out
[harvest report development][harvest-rpt-dev] in the [harvest][harvest] README.

## Usage

`arboretum` is available for download from [PyPI](https://pypi.org/project/auditree-arboretum/).

### Prerequisites

- Supported for execution on OSX and LINUX.
- Supported for execution with Python 3.6 and above.

### Integration

Follow these steps to integrate auditree-arboretum fetchers and checks into your project:

* Add this `auditree-arboretum` package as a dependency in your Python project.
* The following steps can be taken to import individual arboretum fetchers and checks.
  * For a fetcher, add a `fetch_<category>_common.py` module, if one does not already
  exist, in your project's `fetchers` path where the `<category>` is
  the respective category folder within this repo of that fetcher.  Having a separate
  common "category" module guards against name collisions across categories.
  * For a check, add a `test_<category>_common.py` module, if one does not already exist,
  in your project's `checks` path where the `<category>` is the respective category folder
  within this repo of that check.  Having a separate common "category" module guards
  against name collisions across providers and technologies.
  * Import the desired fetcher or check class and the `auditree-framework` will handle
  the rest.

  For example to use the Abandoned Evidence fetcher from the `auditree` category, add
  the following to your `fetch_auditree_common.py`:

  ```python
  from arboretum.auditree.fetchers.fetch_abandoned_evidence import AbandonedEvidenceFetcher
  ```

* `auditree-arboretum` fetchers and checks are designed to execute as part of a downstream
Python project, so you may need to setup your project's configuration in order for the
fetchers and checks to execute as desired.  Each category folder in this repository
includes a README.md that documents each fetcher's and check's configuration.
  * In general `auditree-arboretum` fetchers and checks expect an `org` field with content
  that captures each fetcher's and check's configuration settings.

  For example:

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
  ```

* Finally, for a check, be sure to add the appropriate entry into your project's
``controls.json`` file.  Doing this allows you to group checks together as a control
set which is useful for organizing check notifications and targeted check execution.

  For example to use the Abandoned Evidence check, add something similar to the
  following to your project's `controls.json`:

  ```json
  {
    "arboretum.auditree.checks.test_abandoned_evidence.AbandonedEvidenceCheck": {
      "auditree_evidence": {
        "auditree_control": ["arboretum.auditree"]
      }
    }
  }
  ```

[platform-badge]: https://img.shields.io/badge/platform-osx%20|%20linux-orange.svg
[pre-commit-badge]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
[python-badge]: https://img.shields.io/badge/python-v3.6+-blue.svg
[pre-commit]: https://github.com/pre-commit/pre-commit
[python-dl]: https://www.python.org/downloads/
[lint-test]: https://github.com/ComplianceAsCode/auditree-arboretum/actions?query=workflow%3A%22format+%7C+lint+%7C+test%22
[pypi-upload]: https://github.com/ComplianceAsCode/auditree-arboretum/actions?query=workflow%3A%22PyPI+upload%22
[auditree-framework]: https://github.com/ComplianceAsCode/auditree-framework
[harvest]: https://github.com/ComplianceAsCode/auditree-harvest
[fetcher design principles]: https://complianceascode.github.io/auditree-framework/design-principles.html#compliance-fetchers
[evidence dependency chaining]: https://complianceascode.github.io/auditree-framework/design-principles.html#evidence-dependency-chaining
[check design principles]: https://complianceascode.github.io/auditree-framework/design-principles.html#compliance-checks
[Jinja]: https://palletsprojects.com/p/jinja/
[harvest-rpt-dev]: https://github.com/ComplianceAsCode/auditree-harvest#report-development
