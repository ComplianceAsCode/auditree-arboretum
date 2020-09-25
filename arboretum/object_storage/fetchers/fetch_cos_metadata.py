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
"""COS bucket metadata status fetcher."""

import json
from collections import defaultdict

from compliance.evidence import store_raw_evidence
from compliance.fetch import ComplianceFetcher

from ibmcloud_tools.cos.client import COS

from requests.exceptions import HTTPError

from utilitarian.http import BaseSession


class COSMetadataFetcher(ComplianceFetcher):
    """Fetch Cloud Object Storage (COS) bucket metadata."""

    @classmethod
    def setUpClass(cls):
        """Initialize the fetcher object with configuration settings."""
        cls.cos_config = cls.config.get('org.cos')
        return cls

    @store_raw_evidence('cos/cos_bucket_metadata.json')
    def fetch_cos_encryption(self):
        """Fetch encryption configuration of a bucket from COS."""
        evidence = defaultdict(dict)
        # keep track of bucket's region(s)
        bucket_dict = defaultdict(list)
        for account, account_config in self.cos_config['accounts'].items():
            for region, instances in account_config.items():
                for instance in instances:
                    cos = COS(
                        account=account,
                        creds=self.config.creds,
                        region=region,
                        service_instance=instance
                    )
                    with BaseSession(cos.endpoint) as s:
                        s.headers.update(
                            {'authorization': f'Bearer {cos.iam_token}'}
                        )
                        for bucket in cos.buckets:
                            response = s.head(bucket)
                            try:
                                response.raise_for_status()
                                bucket_dict[bucket].append(region)
                            except HTTPError as he:
                                if he.response.status_code == 404:
                                    self.locker.logger.debug(
                                        f'{bucket} not found in {region}'
                                    )
                                    continue
                                else:
                                    raise he
                            data = dict(response.headers)
                            # These change with each request, so remove to
                            # prevent churn
                            del data['Date']
                            del data['X-Clv-Request-Id']
                            del data['x-amz-request-id']
                            evidence[account][response.url] = data
        for bucket, regions in bucket_dict.items():
            if (len(regions) < 1):
                self.locker.logger.warning(f'{bucket} not found in any region')
            elif (len(regions) > 1):
                self.locker.logger.warning(
                    f'{bucket} found in multiple regions: {regions}'
                )
            else:
                self.locker.logger.debug(
                    f'{bucket} found in region: {regions[0]}'
                )

        return json.dumps(evidence)
