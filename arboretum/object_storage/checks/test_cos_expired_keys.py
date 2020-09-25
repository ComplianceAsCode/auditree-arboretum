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
"""COS bucket encryption key validity checks."""

import json

from compliance.check import ComplianceCheck
from compliance.evidence import DAY, ReportEvidence, with_raw_evidences


class COSBucketEncryptionKeyValidCheck(ComplianceCheck):
    """Check keys used to encrypt buckets are not expired."""

    @property
    def title(self):
        """
        Return the title of the checks.

        :returns: the title of the checks
        """
        return 'COS bucket expired keys check'

    @classmethod
    def setUpClass(cls):
        """Initialize the check object with configuration settings."""
        cls.config.add_evidences(
            [
                ReportEvidence(
                    'cos_bucket_key_valid.md',
                    'cos',
                    DAY,
                    'COS bucket expired keys report'
                )
            ]
        )
        return cls

    @with_raw_evidences('cos/cos_bucket_metadata.json')
    def test_bucket_expired_key(self, buckets_metadata):
        """Check all buckets are using a valid customer key."""
        evidence = json.loads(buckets_metadata.content)
        expired_keys = self.config.get('org.cos.encryption.expired_keys', [])
        found_keys = set()
        for account, buckets in evidence.items():
            for bucket, metadata in buckets.items():
                if metadata['ibm-sse-kp-enabled'] == 'true':
                    key = metadata['ibm-sse-kp-customer-root-key-crn']
                    msg = f'buckets using an expired customer key `{key}`'
                    if key in expired_keys:
                        self.add_failures(
                            f'Account: `{account}`, {msg}', bucket
                        )
                        found_keys.add(key)
        unused_expired_keys = set(expired_keys) - found_keys
        if unused_expired_keys:
            for key in unused_expired_keys:
                self.add_warnings('configured expired key not found', key)

    def get_reports(self):
        """
        Provide the check report name.

        :returns: the report(s) generated for this check.
        """
        return ['cos/cos_bucket_key_valid.md']

    def get_notification_message(self):
        """Notification for the expired key check."""
        return {'subtitle': 'expired encryption key'}
