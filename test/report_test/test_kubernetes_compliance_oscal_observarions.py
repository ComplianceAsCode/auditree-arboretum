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
"""Harvest compliance oscal observations report tests."""

import hashlib
import unittest
import uuid
from unittest.mock import Mock, patch

import arboretum.kubernetes.reports.compliance_oscal_observations as co

# mock uuid so that generated uuid's will match expected results
uuid_mock1 = Mock(
    return_value=uuid.UUID('56666738-0f9a-4e38-9aac-c0fad00a5821')
)


class TestKubernetesComplianceOscalObservations(unittest.TestCase):
    """Test ComplianceOscalObservations."""

    def test_report_filename(self):
        """Ensure check results summary filename property is set."""
        report = co.ComplianceOscalObservations(
            'https://repo', 'creds', 'branch', 'repo-path'
        )
        self.assertEqual(
            report.report_filename, 'compliance_oscal_observations.json'
        )

    def test_generate_report_exception_no_cluster_resource_content(self):
        """Ensure proper handling of no cluster_resource content."""
        report = co.ComplianceOscalObservations(
            'https://repo',
            'creds',
            'branch',
            'repo-path',
            cluster_resource='bogus'
        )
        with self.assertRaises(RuntimeError) as e:
            report.generate_report()
        self.assertEqual(str(e.exception), 'No report content.')

    def test_generate_report_bad_dates(self):
        """Ensure proper handling bad start and end dates."""
        report = co.ComplianceOscalObservations(
            'https://repo',
            'creds',
            'branch',
            'repo-path',
            start='20210101',
            end='20201231'
        )
        with self.assertRaises(ValueError) as e:
            report.generate_report()
        self.assertEqual(
            str(e.exception), 'Cannot have start date before end date.'
        )

    @patch(target='uuid.uuid4', new=uuid_mock1)
    def test_generate_report(self):
        """Ensure proper report creation."""
        with open('./test/fixtures/kubernetes_cluster_resource.json',
                  'r') as f:
            kubernetes_cluster_resource = f.read()
        tgt = 'arboretum.kubernetes.reports.compliance_oscal_observations.'
        tgt += 'ComplianceOscalObservations.get_file_content'
        with patch(tgt, Mock(side_effect=[kubernetes_cluster_resource])):
            report = co.ComplianceOscalObservations(
                'https://repo', 'creds', 'branch', 'repo-path'
            )
            result = report.generate_report()
        self.assertEqual(
            'ff4b5c1576e226aca4108b3a6a335969',
            hashlib.md5(result.encode('utf-8')).hexdigest()
        )

    @patch(target='uuid.uuid4', new=uuid_mock1)
    def test_generate_report_with_metadata(self):
        """Ensure proper report creation with oscal metadata."""
        with open('./test/fixtures/compliance_oscal_metadata.yaml', 'r') as f:
            compliance_oscal_metadata = f.read()
        with open('./test/fixtures/kubernetes_cluster_resource.json',
                  'r') as f:
            kubernetes_cluster_resource = f.read()
        tgt = 'arboretum.kubernetes.reports.compliance_oscal_observations.'
        tgt += 'ComplianceOscalObservations.get_file_content'
        with patch(tgt,
                   Mock(side_effect=[kubernetes_cluster_resource,
                                     compliance_oscal_metadata])):
            report = co.ComplianceOscalObservations(
                'https://github.mycorp.com/myuser/evidence-locker',
                'creds',
                'branch',
                'repo-path',
                oscal_metadata='compliance_oscal_metadata.yaml'
            )
            result = report.generate_report()
        self.assertEqual(
            '28f797591fcf61f0edb6f4ad17a0a98d',
            hashlib.md5(result.encode('utf-8')).hexdigest()
        )

    def test_generate_report_no_resources(self):
        """Test no 'resources' found."""
        with open('./test/fixtures/kubernetes_cluster_resource.json',
                  'r') as f:
            kubernetes_cluster_resource = f.read().replace(
                'resources', 'bogus'
            )
        self._expect_no_report_content(kubernetes_cluster_resource)

    def test_generate_report_no_kind(self):
        """Test no 'kind' found."""
        with open('./test/fixtures/kubernetes_cluster_resource.json',
                  'r') as f:
            kubernetes_cluster_resource = f.read().replace('kind', 'bogus')
        self._expect_no_report_content(kubernetes_cluster_resource)

    def test_generate_report_no_configmap(self):
        """Test no 'ConfigMap' found."""
        with open('./test/fixtures/kubernetes_cluster_resource.json',
                  'r') as f:
            kubernetes_cluster_resource = f.read().replace(
                'ConfigMap', 'bogus'
            )
        self._expect_no_report_content(kubernetes_cluster_resource)

    def test_generate_report_no_data(self):
        """Test no 'data' found."""
        with open('./test/fixtures/kubernetes_cluster_resource.json',
                  'r') as f:
            kubernetes_cluster_resource = f.read().replace('data', 'bogus')
        self._expect_no_report_content(kubernetes_cluster_resource)

    def test_generate_report_no_results(self):
        """Test no 'results' found."""
        with open('./test/fixtures/kubernetes_cluster_resource.json',
                  'r') as f:
            kubernetes_cluster_resource = f.read().replace('results', 'bogus')
        self._expect_no_report_content(kubernetes_cluster_resource)

    def test_generate_report_no_metadata(self):
        """Test no 'metadata' found."""
        with open('./test/fixtures/kubernetes_cluster_resource.json',
                  'r') as f:
            kubernetes_cluster_resource = f.read().replace('metadata', 'bogus')
        self._expect_no_report_content(kubernetes_cluster_resource)

    def test_generate_report_no_name(self):
        """Test no 'name' found."""
        with open('./test/fixtures/kubernetes_cluster_resource.json',
                  'r') as f:
            kubernetes_cluster_resource = f.read().replace('name', 'bogus')
        self._expect_no_report_content(kubernetes_cluster_resource)

    def _expect_no_report_content(self, kubernetes_cluster_resource):
        """Expect 'No report content.' exception."""
        tgt = 'arboretum.kubernetes.reports.compliance_oscal_observations.'
        tgt += 'ComplianceOscalObservations.get_file_content'
        with patch(tgt, Mock(side_effect=[kubernetes_cluster_resource])):
            report = co.ComplianceOscalObservations(
                'https://repo', 'creds', 'branch', 'repo-path'
            )
            with self.assertRaises(RuntimeError) as e:
                report.generate_report()
            self.assertEqual(str(e.exception), 'No report content.')
