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
"""Compliance execution configuration check."""

import json

from compliance.check import ComplianceCheck
from compliance.evidence import DAY, ReportEvidence, with_raw_evidences


class ComplianceConfigCheck(ComplianceCheck):
    """
    Compare running & historical configuration.

    This check compares configuration captured by the fetcher as evidence with
    the current configuration being used by the checks.
    """

    @property
    def title(self):
        """
        Provide the title of the checks.

        :returns: the title of the checks
        """
        return 'Compliance Configuration'

    @classmethod
    def setUpClass(cls):
        """Initialize the check object with configuration settings."""
        cls.config.add_evidences(
            [
                ReportEvidence(
                    'compliance_config.md',
                    'auditree',
                    DAY,
                    'Compliance repository configuration settings report.'
                )
            ]
        )

        return cls

    @with_raw_evidences('auditree/compliance_config.json')
    def test_compliance_configuration(self, evidence):
        """Check that current config matches with config evidence."""
        evidence_config = json.loads(evidence.content)
        if evidence_config != self.config.raw_config:
            evidence = json.dumps(evidence_config, indent=2).split('\n')
            config = json.dumps(self.config.raw_config, indent=2).split('\n')
            self.add_failures(
                'Differences found',
                {
                    'Fetcher Configuration': evidence,
                    'Check Configuration': config
                }
            )

    def get_reports(self):
        """
        Provide the check report name.

        :returns: the report(s) generated for this check
        """
        return ['auditree/compliance_config.md']

    def get_notification_message(self):
        """
        Compliance configuration check notifier.

        :returns: notification dictionary.
        """
        return {'body': None}
