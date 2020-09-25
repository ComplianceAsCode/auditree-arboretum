# -*- coding:utf-8; mode:python -*-
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
"""COS bucket encryption status checks."""

import json

from compliance.check import ComplianceCheck
from compliance.evidence import DAY, ReportEvidence, with_raw_evidences


class COSBucketEncryptionKeyCheck(ComplianceCheck):
    """Check all of the buckets are encrypted with a customer key."""

    @property
    def title(self):
        """
        Return the title of the checks.

        :returns: the title of the checks
        """
        return 'COS bucket encryption key check'

    @classmethod
    def setUpClass(cls):
        """Initialize the check object with configuration settings."""
        cls.config.add_evidences(
            [
                ReportEvidence(
                    'cos_bucket_encryption.md',
                    'cos',
                    DAY,
                    'COS bucket encryption report'
                )
            ]
        )
        return cls

    @with_raw_evidences('cos/cos_bucket_metadata.json')
    def test_bucket_customer_key_encryption(self, buckets_metadata):
        """Check all buckets are encrypted with customer key."""
        evidence = json.loads(buckets_metadata.content)
        excluded = self.config.get('org.cos.encryption.exclude', [])
        for account, buckets in evidence.items():
            for bucket, metadata in buckets.items():
                msg = None
                kp_enabled = metadata.get('ibm-sse-kp-enabled')
                if kp_enabled is None:
                    msg = 'no encryption data for buckets'
                elif kp_enabled != 'true':
                    msg = (
                        'buckets not encrypted with customer key '
                        '(ibm-sse-kp-enabled is false)'
                    )
                if msg:
                    if bucket in excluded:
                        self.add_warnings(
                            f'Account: `{account}`, {msg} but is excluded',
                            bucket
                        )
                    else:
                        self.add_failures(
                            f'Account: `{account}`, {msg}', bucket
                        )

    def get_reports(self):
        """
        Provide the check report name.

        :returns: the report(s) generated for this check.
        """
        return ['cos/cos_bucket_encryption.md']

    def get_notification_message(self):
        """Notification for the non-customer key check."""
        return {'subtitle': 'buckets without customer encryption key'}
