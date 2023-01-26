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
"""Evidence locker empty evidences check."""
from compliance.check import ComplianceCheck
from compliance.evidence import DAY, ReportEvidence


class EmptyEvidenceCheck(ComplianceCheck):
    """
    Empty evidence check.

    This check finds all evidence in the evidence locker that has no content.
    """

    @property
    def title(self):
        """
        Return the title of the checks.

        :returns: the title of the checks
        """
        return "Empty Evidence"

    @classmethod
    def setUpClass(cls):
        """Initialize the check object with configuration settings."""
        cls.config.add_evidences(
            [
                ReportEvidence(
                    "empty_evidence.md",
                    "auditree",
                    DAY,
                    "Evidence locker empty evidence report.",
                )
            ]
        )
        return cls

    def test_empty_evidence(self):
        """Check for evidence that has no content."""
        exceptions = self.config.get("org.auditree.empty_evidence.exceptions", [])
        for ev_path in self.locker.get_empty_evidences():
            if ev_path not in exceptions:
                self.add_failures("Empty Evidence", f"`{ev_path}`")
            else:
                self.add_warnings("Expected Empty Evidence", f"`{ev_path}`")

    def get_reports(self):
        """
        Provide the check report name.

        :returns: the report(s) generated for this check.
        """
        return ["auditree/empty_evidence.md"]

    def get_notification_message(self):
        """
        Empty evidence check notifier.

        :returns: notification dictionary.
        """
        return {"body": None}
