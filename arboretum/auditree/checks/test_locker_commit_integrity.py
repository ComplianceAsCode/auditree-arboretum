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
"""Evidence locker commit integrity checks."""

from urllib.parse import urlparse

from arboretum.auditree.evidences.repo_branch_protection import (
    RepoBranchProtectionEvidence,
)
from arboretum.auditree.evidences.repo_commit import RepoCommitEvidence

from compliance.check import ComplianceCheck
from compliance.evidence import DAY, ReportEvidence, evidences


class LockerCommitIntegrityCheck(ComplianceCheck):
    """Monitor the integrity of evidence locker repository commits."""

    @property
    def title(self):
        """
        Return the title of the checks.

        :returns: the title of the checks
        """
        return "Locker Commit Integrity"

    @classmethod
    def setUpClass(cls):
        """Initialize the check object with configuration settings."""
        cls.config.add_evidences(
            [
                ReportEvidence(
                    "locker_commit_integrity.md",
                    "auditree",
                    DAY,
                    "Evidence locker commit integrity report.",
                )
            ]
        )
        return cls

    def test_recent_commit_integrity(self):
        """Check that recent commits are signed."""
        locker_branches = self.config.get(
            "org.auditree.locker_integrity.branches",
            self.config.get(
                "org.auditree.repo_integrity.branches",
                {self.config.get("locker.repo_url"): ["master"]},
            ),
        )
        for locker_url, branches in locker_branches.items():
            parsed = urlparse(locker_url)
            service = "gh"
            if "gitlab" in parsed.hostname:
                service = "gl"
            elif "bitbucket" in parsed.hostname:
                service = "bb"
            repo = parsed.path.strip("/")
            for branch in branches:
                filename = [
                    service,
                    repo.lower().replace("/", "_").replace("-", "_"),
                    branch.lower().replace("-", "_"),
                    "recent_commits.json",
                ]
                path = f'raw/auditree/{"_".join(filename)}'
                with evidences(self, path) as raw:
                    commits = RepoCommitEvidence.from_evidence(raw)
                    for commit in commits.signed_status:
                        if not commit["signed"]:
                            self.add_failures(
                                "Locker Recent Commits - (Unsigned)",
                                (
                                    f'[{commit["sha"][:8]}]({commit["url"]}) '
                                    f"commit in `{locker_url}` "
                                    f"`{branch}` branch."
                                ),
                            )

    def test_branch_protection_commit_integrity(self):
        """Check that branch protection requires signed commits."""
        locker_branches = self.config.get(
            "org.auditree.locker_integrity.branches",
            self.config.get(
                "org.auditree.repo_integrity.branches",
                {self.config.get("locker.repo_url"): ["master"]},
            ),
        )
        for locker_url, branches in locker_branches.items():
            parsed = urlparse(locker_url)
            service = "gh"
            if "gitlab" in parsed.hostname:
                service = "gl"
            elif "bitbucket" in parsed.hostname:
                service = "bb"
            repo = parsed.path.strip("/")
            for branch in branches:
                filename = [
                    service,
                    repo.lower().replace("/", "_").replace("-", "_"),
                    branch.lower().replace("-", "_"),
                    "branch_protection.json",
                ]
                path = f'raw/auditree/{"_".join(filename)}'
                with evidences(self, path) as raw:
                    evidence = RepoBranchProtectionEvidence.from_evidence(raw)
                    if not evidence.signed_commits_required:
                        self.add_failures(
                            ("Locker Branch Protection - " "(Signed Commits Disabled)"),
                            f"`{locker_url}` `{branch}` branch.",
                        )

    def get_reports(self):
        """
        Provide the check report name.

        :returns: the report(s) generated for this check
        """
        return ["auditree/locker_commit_integrity.md"]

    def msg_recent_commit_integrity(self):
        """
        Evidence locker recent commits integrity check notifier.

        :returns: notification dictionary
        """
        return {"subtitle": "Locker signed commits", "body": None}

    def msg_branch_protection_commit_integrity(self):
        """
        Evidence locker branch protection commit integrity check notifier.

        :returns: notification dictionary
        """
        return {"subtitle": "Locker require commit signatures", "body": None}
