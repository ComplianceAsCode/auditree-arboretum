# -*- mode:python; coding:utf-8 -*-
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
"""ICD backups fetcher."""
import json
from datetime import datetime, timedelta
from urllib.parse import quote

from arboretum.common.iam_ibm_utils import get_tokens
from arboretum.common.ibm_constants import DB_API_URL

from compliance.evidence import DAY, RawEvidence
from compliance.evidence import get_evidence_dependency, raw_evidence
from compliance.fetch import ComplianceFetcher
from compliance.utils.http import BaseSession


class DatabaseBackupsFetcher(ComplianceFetcher):
    """Fetches IBM Cloud Databases backups lists."""

    @classmethod
    def setUpClass(cls):
        """Initialize object from config file."""
        cls.api_sessions = {}
        cls.accounts = cls.config.get('org.icd.list.accounts')
        for acct in cls.accounts:
            acct_name = acct['account_name']
            cls.config.add_evidences(
                [
                    RawEvidence(
                        f'backups_{acct_name}.json',
                        'icd',
                        DAY,
                        'list of database backups for account'
                    )
                ]
            )

        return cls

    @classmethod
    def tearDownClass(cls):
        """Clean up and housekeeping."""
        for session in cls.api_sessions.values():
            session.close()

    def fetch_backups(self):
        """Fetch IBM Cloud Database backups per account."""
        now = datetime.utcnow()
        for acct in self.accounts:
            acct_name = acct['account_name']
            evidence_path_main = f'raw/icd/backups_{acct_name}.json'
            evidence_path_dep = f'raw/icd/databases_{acct_name}.json'
            start_time = now - timedelta(days=1)

            evidence_metadata = self.locker.get_evidence_metadata(
                evidence_path_main
            )

            if evidence_metadata:
                start_time = datetime.strptime(
                    evidence_metadata['last_update'], '%Y-%m-%dT%H:%M:%S.%f'
                )

            with raw_evidence(self.locker, evidence_path_main) as evidence:
                if evidence:
                    db_list_raw_evidence = get_evidence_dependency(
                        evidence_path_dep, self.locker
                    )

                    backups = []
                    db_items = json.loads(db_list_raw_evidence.content)
                    if not isinstance(db_items, list):
                        db_items = [db_items]

                    for db_item in db_items:
                        for db in db_item['resources']:
                            backups.extend(
                                self._get_backups_list_later_than(
                                    acct_name, db, start_time
                                )
                            )

                    evidence.set_content(json.dumps(backups))

    def _get_backups_list_later_than(self, account, db_obj, start_time):
        backups_list = self._get_ibmcloud_db_backups_list(account, db_obj)

        if 'backups' in backups_list:
            return [
                backup for backup in backups_list['backups']
                if start_time < datetime.
                strptime(backup['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
            ]

        return []

    def _get_ibmcloud_db_backups_list(self, account, db_obj):

        # get session for the region if needed
        region = db_obj['region_id']
        if region not in self.api_sessions.keys():
            self.api_sessions[region] = BaseSession(DB_API_URL.format(region))
            api_key = getattr(
                self.config.creds['ibm_cloud'], f'{account}_api_key'
            )
            self.api_sessions[region].headers.update(
                {
                    'Accept': 'application/json',
                    'Authorization': f'Bearer {get_tokens(api_key)[0]}'
                }
            )

        # get database backups list
        # https://cloud.ibm.com/apidocs/cloud-databases-api/
        #                       cloud-databases-api-v4#getdeploymentbackups
        escaped_crn = quote(db_obj['crn'], safe='')
        resp = self.api_sessions[region].get(
            f'/v4/ibm/deployments/{escaped_crn}/backups'
        )
        resp.raise_for_status()
        return resp.json()
