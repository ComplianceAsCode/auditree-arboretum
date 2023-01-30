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
"""Execution environment Python packages fetchers."""

import json

from arboretum.auditree.evidences.python_package_release import PackageReleaseEvidence
from arboretum.common.constants import PYPI_RSS_BASE_URL

from compliance.evidence import DAY, RawEvidence, store_raw_evidence
from compliance.fetch import ComplianceFetcher

from pkg_resources import working_set


class PythonPackageFetcher(ComplianceFetcher):
    """Fetch the current environment's Python package list."""

    @classmethod
    def setUpClass(cls):
        """Initialize the fetcher object with configuration settings."""
        cls.config.add_evidences(
            [
                RawEvidence(
                    "python_packages.json", "auditree", DAY, "Python Package List"
                ),
                PackageReleaseEvidence(
                    "auditree_arboretum_releases.xml",
                    "auditree",
                    DAY,
                    "Auditree Arboretum PyPI releases",
                ),
                PackageReleaseEvidence(
                    "auditree_framework_releases.xml",
                    "auditree",
                    DAY,
                    "Auditree Framework PyPI releases",
                ),
            ]
        )
        headers = {"Content-Type": "application/xml", "Accept": "application/xml"}
        cls.session(PYPI_RSS_BASE_URL, **headers)
        return cls

    @store_raw_evidence("auditree/python_packages.json")
    def fetch_python_package_list(self):
        """Fetch the Python packages in the current virtual environment."""
        packages = {}
        for dist in working_set:
            packages[dist.project_name] = dist.version

        return json.dumps(packages)

    @store_raw_evidence("auditree/auditree_arboretum_releases.xml")
    def fetch_auditree_arboretum_releases(self):
        """Fetch the auditree-arboretum package releases."""
        return self._fetch_pypi_releases("auditree-arboretum")

    @store_raw_evidence("auditree/auditree_framework_releases.xml")
    def fetch_auditree_framework_releases(self):
        """Fetch the auditree-framework package releases."""
        return self._fetch_pypi_releases("auditree-framework")

    @store_raw_evidence("auditree/auditree_harvest_releases.xml")
    def fetch_auditree_harvest_releases(self):
        """Fetch the auditree-harvest package releases."""
        return self._fetch_pypi_releases("auditree-harvest")

    def _fetch_pypi_releases(self, package_name):
        resp = self.session().get(f"{package_name}/releases.xml")
        resp.raise_for_status()
        return resp.text
