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
"""Evidence locker abandoned evidence fetcher."""

import json

from compliance.evidence import DAY, RawEvidence, store_raw_evidence
from compliance.fetch import ComplianceFetcher
from compliance.locker import AE_DEFAULT


class AbandonedEvidenceFetcher(ComplianceFetcher):
    """Fetch the evidence locker's abandoned evidence files."""

    @classmethod
    def setUpClass(cls):
        """Initialize the fetcher object with configuration settings."""
        cls.config.add_evidences(
            [
                RawEvidence(
                    'abandoned_evidence.json',
                    'auditree',
                    DAY,
                    'Abandoned evidence'
                )
            ]
        )

        return cls

    @store_raw_evidence('auditree/abandoned_evidence.json')
    def fetch_abandoned_evidence(self):
        """Fetch the evidence locker abandoned evidence."""
        exception_path = 'org.auditree.abandoned_evidence.exceptions'
        exceptions = self.config.get(exception_path, {})
        ae_paths = self.locker.get_abandoned_evidences(
            self.config.get(
                'org.auditree.abandoned_evidence.threshold', AE_DEFAULT
            )
        )
        abandoned_evidence = {'abandoned': [], 'exceptions': {}}
        for ae in ae_paths:
            if ae in exceptions.keys():
                abandoned_evidence['exceptions'][ae] = exceptions[ae]
            else:
                abandoned_evidence['abandoned'].append(ae)
        return json.dumps(abandoned_evidence)
