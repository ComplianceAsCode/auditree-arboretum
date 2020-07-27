# -*- coding:utf-8; mode:python -*-
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
