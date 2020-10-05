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
"""Evidence locker abandoned evidences check."""

import json
from datetime import datetime, timedelta

from arboretum.common.utils import parse_seconds

from compliance.check import ComplianceCheck
from compliance.evidence import DAY, ReportEvidence
from compliance.locker import (
    AE_DEFAULT, EvidenceNotFoundError, HistoricalEvidenceNotFoundError
)


class AbandonedEvidenceCheck(ComplianceCheck):
    """
    Abandoned evidence check.

    This check finds all evidence in the evidence locker that has not been
    updated within a given timeframe.
    """

    @property
    def title(self):
        """
        Return the title of the checks.

        :returns: the title of the checks
        """
        return getattr(self, '_title', 'Abandoned Evidence')

    @property
    def formatted_threshold(self):
        """
        Return a formatted abandoned evidence threshold as a string.

        :returns: the AE threshold as 'd days, h hours, m minutes, s seconds'
        """
        return parse_seconds(
            self.config.get(
                'org.auditree.abandoned_evidence.threshold', AE_DEFAULT
            )
        )

    @classmethod
    def setUpClass(cls):
        """Initialize the check object with configuration settings."""
        cls.config.add_evidences(
            [
                ReportEvidence(
                    'abandoned_evidence.md',
                    'auditree',
                    DAY,
                    'Evidence locker abandoned evidence report.'
                )
            ]
        )
        return cls

    def test_abandoned_evidence(self):
        """Check for evidence that may have been abandoned."""
        ignore_history = self.config.get(
            'org.auditree.abandoned_evidence.ignore_history', False
        )
        if ignore_history:
            self._test_without_history()
        else:
            ae_path = 'raw/auditree/abandoned_evidence.json'
            current_evidence = None
            previous_evidence = None
            try:
                current_evidence = self.locker.get_evidence(ae_path)
                self.add_evidence_metadata(current_evidence.path)
                previous_evidence = self.get_historical_evidence(
                    ae_path, datetime.utcnow() - timedelta(days=1)
                )
                self._test_with_history(current_evidence, previous_evidence)
            except EvidenceNotFoundError:
                # For backward compatibility.
                self._test_without_history()
            except HistoricalEvidenceNotFoundError:
                self._test_with_history(current_evidence, previous_evidence)

    def _test_with_history(self, current_evidence, previous_evidence=None):
        self._title = 'Latest Abandoned Evidence'
        current = json.loads(current_evidence.content)
        previous = {'abandoned': [], 'exceptions': {}}
        if previous_evidence:
            previous = json.loads(previous_evidence.content)
        for ae_path in current['abandoned']:
            if ae_path not in previous['abandoned']:
                metadata = self.locker.get_evidence_metadata(ae_path) or {}
                ae = {
                    'ae_path': ae_path,
                    'last_update': metadata.get('last_update', 'UNAVAILABLE')
                }
                self.add_failures('Abandoned evidence', ae)
        for ae_path, reason in current['exceptions'].items():
            if ae_path not in previous['exceptions'].keys():
                metadata = self.locker.get_evidence_metadata(ae_path) or {}
                ae = {
                    'ae_path': ae_path,
                    'last_update': metadata.get('last_update', 'UNAVAILABLE'),
                    'exception_reason': reason
                }
                self.add_warnings('Exceptions', ae)

    def _test_without_history(self):
        """For backward compatibility."""
        ae_paths = self.locker.get_abandoned_evidences(
            self.config.get(
                'org.auditree.abandoned_evidence.threshold', AE_DEFAULT
            )
        )
        exceptions_path = 'org.auditree.abandoned_evidence.exceptions'
        exceptions = self.config.get(exceptions_path, {})
        for ae_path in ae_paths:
            metadata = self.locker.get_evidence_metadata(ae_path) or {}
            ae = {
                'ae_path': ae_path,
                'last_update': metadata.get('last_update', 'UNAVAILABLE')
            }
            if ae_path in exceptions.keys():
                ae['exception_reason'] = exceptions[ae_path]
                self.add_warnings('Exceptions', ae)
            else:
                self.add_failures('Abandoned evidence', ae)

    def get_reports(self):
        """
        Provide the check report name.

        :returns: the report(s) generated for this check.
        """
        return ['auditree/abandoned_evidence.md']

    def get_notification_message(self):
        """
        Abandoned evidence check notifier.

        :returns: notification dictionary.
        """
        return {'body': None}
