# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Execution environment Python packages checks."""

import json
from datetime import datetime, timedelta

from arboretum.auditree.evidences.python_package_release import (
    PackageReleaseEvidence
)

from compliance.check import ComplianceCheck
from compliance.evidence import DAY, ReportEvidence, with_raw_evidences


class PythonPackageCheck(ComplianceCheck):
    """Compare the software versions used in Auditree execution."""

    @property
    def title(self):
        """
        Return the title of the checks.

        :returns: the title of the checks
        """
        return 'Python Packages'

    @classmethod
    def setUpClass(cls):
        """Initialize the check object with configuration settings."""
        cls.config.add_evidences(
            [
                ReportEvidence(
                    'python_packages.md',
                    'auditree',
                    DAY,
                    'Execution environment Python packages report.'
                )
            ]
        )

        return cls

    @with_raw_evidences('auditree/python_packages.json')
    def test_python_package_deltas(self, today):
        """Check the last two Python environments against each other."""
        yesterday = None
        yesterday_dt = datetime.utcnow() - timedelta(days=1)
        try:
            yesterday = self.get_historical_evidence(
                'raw/auditree/python_packages.json', yesterday_dt
            )
        except ValueError:
            self.add_warnings(
                'Python Package Deltas',
                (
                    'No evidence found on or prior '
                    f'to {yesterday_dt.strftime("%b %d, %Y")}'
                )
            )
            return
        today_pkgs = json.loads(today.content)
        yesterday_pkgs = json.loads(yesterday.content)
        for pkg, ver in today_pkgs.items():
            if pkg not in yesterday_pkgs.keys():
                self.add_warnings('New Packages', f'{pkg} version {ver}')
            elif ver != yesterday_pkgs[pkg]:
                self.add_warnings(
                    'Package Version Changes',
                    (
                        f'{pkg} previous version {yesterday_pkgs[pkg]}, '
                        f'current version {ver}'
                    )
                )
        for pkg in set(yesterday_pkgs.keys()) - set(today_pkgs.keys()):
            self.add_warnings(
                'Removed Packages', f'{pkg} version {yesterday_pkgs[pkg]}'
            )

    @with_raw_evidences(
        'auditree/python_packages.json',
        'auditree/auditree_arboretum_releases.xml'
    )
    def test_auditree_arboretum_version(self, packages, releases):
        """Check auditree-arboretum version matches latest release."""
        self._test_versions(packages, releases, 'auditree-arboretum')

    @with_raw_evidences(
        'auditree/python_packages.json',
        'auditree/auditree_framework_releases.xml'
    )
    def test_auditree_framework_version(self, packages, releases):
        """Check auditree-framework version matches latest release."""
        self._test_versions(packages, releases, 'auditree-framework')

    @with_raw_evidences(
        'auditree/python_packages.json',
        'auditree/auditree_harvest_releases.xml'
    )
    def test_auditree_harvest_version(self, packages, releases):
        """Check auditree-harvest version matches latest release."""
        self._test_versions(packages, releases, 'auditree-harvest')

    def _test_versions(self, packages, releases, package):
        latest = PackageReleaseEvidence.from_evidence(releases).latest_release
        version_used = json.loads(packages.content).get(package)
        if version_used != latest:
            self.add_warnings(
                'Latest Version Violation',
                (
                    f'{package} latest version {latest}, '
                    f'version used {version_used}'
                )
            )

    def get_reports(self):
        """
        Provide the check report name.

        :returns: the report(s) generated for this check
        """
        return ['auditree/python_packages.md']

    def msg_python_package_deltas(self):
        """
        Python Packages deltas check notifier.

        :returns: notification dictionary
        """
        return {'subtitle': 'Python package deltas', 'body': None}

    def msg_auditree_arboretum_version(self):
        """
        Python Packages auditree-arboretum check notifier.

        :returns: notification dictionary
        """
        return {'subtitle': 'auditree-arboretum version', 'body': None}

    def msg_auditree_framework_version(self):
        """
        Python Packages auditree-framework check notifier.

        :returns: notification dictionary
        """
        return {'subtitle': 'auditree-framework version', 'body': None}

    def msg_auditree_harvest_version(self):
        """
        Python Packages auditree-harvest check notifier.

        :returns: notification dictionary
        """
        return {'subtitle': 'auditree-harvest version', 'body': None}
