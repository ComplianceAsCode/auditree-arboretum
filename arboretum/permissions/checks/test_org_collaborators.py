# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""Repository organization/owner collaborators check."""

from compliance.check import ComplianceCheck
from compliance.evidence import DAY, ReportEvidence, evidences
from compliance.utils.data_parse import get_sha256_hash


class OrgCollaboratorsCheck(ComplianceCheck):
    """Checks for repository organization/owner collaborators."""

    @property
    def title(self):
        """
        Return the title of the checks.

        :returns: the title of the checks
        """
        return "Repository Organization/Owner Collaborators"

    @classmethod
    def setUpClass(cls):
        """Initialize the check object with configuration settings."""
        cls.config.add_evidences(
            [
                ReportEvidence(
                    "org_collaborators.md",
                    "permissions",
                    DAY,
                    "Repository organization collaborators report.",
                )
            ]
        )
        return cls

    def test_org_direct_collaborators(self):
        """Check that there are no direct collaborators in the org repos."""
        orgs = self.config.get("org.permissions.org_integrity.orgs")
        evidence_paths = {}
        exceptions = {}
        for org in orgs:
            if "direct" not in org.get("collaborator_types", []):
                continue
            host, org_name = org["url"].rsplit("/", 1)
            service = "gh"
            if "gitlab" in host:
                service = "gl"
            elif "bitbucket" in host:
                service = "bb"

            url_hash = get_sha256_hash([org["url"]], 10)
            filename = f"{service}_direct_collaborators_{url_hash}.json"
            path = f"raw/permissions/{filename}"
            evidence_paths[org_name] = path
            exceptions[org_name] = org.get("exceptions", [])
        with evidences(self, evidence_paths) as raws:
            self._generate_results(raws, exceptions)

    def _generate_results(self, evidences, exceptions):
        for org, ev in evidences.items():
            for repo in ev.content_as_json:
                all_users = [u["login"] for u in ev.content_as_json[repo]]
                if not all_users:
                    continue
                exception_users = [
                    e["user"]
                    for e in exceptions[org]
                    if "repos" not in e.keys() or repo in e["repos"]
                ]
                failed_users = set(all_users) - set(exception_users)
                warning_users = set(all_users).intersection(exception_users)
                if failed_users:
                    self.add_failures(
                        "unexpected-org-collaborators",
                        {"org": org, "repo": repo, "users": failed_users},
                    )
                if warning_users:
                    self.add_warnings(
                        "allowed-org-collaborators",
                        {"org": org, "repo": repo, "users": warning_users},
                    )

    def get_notification_message(self):
        """
        Repository organization collaborators check notifier.

        :returns: notification dictionary
        """
        return {"subtitle": "Repository organization collaborators", "body": None}

    def get_reports(self):
        """
        Provide the check report name.

        :returns: the report(s) generated for this check
        """
        return ["permissions/org_collaborators.md"]
