[![OS Compatibility][platform-badge]](#prerequisites)
[![Python Compatibility][python-badge]][python-dl]
[![pre-commit][pre-commit-badge]][pre-commit]
[![Code validation](https://github.com/ComplianceAsCode/auditree-arboretum/workflows/format%20%7C%20lint%20%7C%20test/badge.svg)][lint-test]
[![Upload Python Package](https://github.com/ComplianceAsCode/auditree-arboretum/workflows/PyPI%20upload/badge.svg)][pypi-upload]

# auditree-arboretum

The Auditree common fetchers, checks and harvest reports library.

## Introduction

Auditree Arboretum is a Python library of common compliance fetchers, checks &amp; harvest
reports built upon the [Auditree compliance automation framework][auditree-framework].

## Prerequisites

- Supported for execution on OSX and LINUX.
- Supported for execution with Python 3.6 and above.

Python 3 must be installed, it can be downloaded from the [Python][python-dl]
site or installed using your package manager.

Python version can be checked with:

```sh
python --version
```

or

```sh
python3 --version
```

`arboretum` is available for download from [PyPI](https://pypi.org/project/auditree-arboretum/).

[platform-badge]: https://img.shields.io/badge/platform-osx%20|%20linux-orange.svg
[pre-commit-badge]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
[python-badge]: https://img.shields.io/badge/python-v3.6+-blue.svg
[pre-commit]: https://github.com/pre-commit/pre-commit
[python-dl]: https://www.python.org/downloads/
[lint-test]: https://github.com/ComplianceAsCode/auditree-arboretum/actions?query=workflow%3A%22format+%7C+lint+%7C+test%22
[pypi-upload]: https://github.com/ComplianceAsCode/auditree-arboretum/actions?query=workflow%3A%22PyPI+upload%22
[auditree-framework]: https://github.com/ComplianceAsCode/auditree-framework
