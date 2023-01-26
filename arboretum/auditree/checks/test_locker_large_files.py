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
"""Evidence locker large files check."""
from compliance.check import ComplianceCheck
from compliance.evidence import DAY, ReportEvidence
from compliance.locker import LF_DEFAULT, MB


class LargeFilesCheck(ComplianceCheck):
    """
    Evidence locker large files check.

    This check finds all large FILES in the evidence locker.
    """

    @property
    def title(self):
        """
        Return the title of the checks.

        :returns: the title of the checks
        """
        return "Large Evidence Locker Files"

    @classmethod
    def setUpClass(cls):
        """Initialize the check object with configuration settings."""
        cls.config.add_evidences(
            [
                ReportEvidence(
                    "locker_large_files.md",
                    "auditree",
                    DAY,
                    "Evidence locker large files report.",
                )
            ]
        )
        return cls

    def test_large_files(self):
        """Check for large files."""
        lf_size = self.config.get("locker.large_file_threshold", LF_DEFAULT)
        warn_size = 0.8 * lf_size
        for f_path, f_size in self.locker.get_large_files(warn_size).items():
            if f_size > lf_size:
                # Fail if file size is over the large file threshold
                self.add_failures(
                    "Large Files:", f"`{f_path}` - {_size_to_str(f_size)}"
                )
            elif f_size > warn_size:
                # Warn if file size is within 20% of the large file threshold
                self.add_warnings(
                    "Large Files (almost):", f"`{f_path}` - {_size_to_str(f_size)}"
                )

    def get_reports(self):
        """
        Provide the check report name.

        :returns: the report(s) generated for this check.
        """
        return ["auditree/locker_large_files.md"]

    def get_notification_message(self):
        """
        Large files check notifier.

        :returns: notification dictionary.
        """
        return {"body": None}


def _size_to_str(size):
    formatted_size = f"{size/MB:.1f} MB"
    if formatted_size == "0.0 MB":
        formatted_size = f"{str(size)} Bytes"
    return formatted_size
