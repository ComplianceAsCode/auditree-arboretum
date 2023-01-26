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
"""Arboretum Kubernetes common utility module tests."""

import unittest
from unittest.mock import MagicMock

from arboretum.common.kube_utils import get_cluster_resources

from requests import HTTPError


class KubernetesUtilTest(unittest.TestCase):
    """Arboretum Kubernetes common utility module tests."""

    def setUp(self):
        """Initialize test objects."""
        self.session = MagicMock()
        self.resp = MagicMock()
        self.data = {"foo", "bar"}
        self.resp.json = MagicMock(return_value={"items": self.data})

    def test_get_cluster_resources_success_core_api(self):
        """Ensure that core API resources can be retrieved."""
        self.resp.raise_for_status = MagicMock()
        self.session.get = MagicMock(return_value=self.resp)
        resource_type = "r1"
        verify = True
        resources = get_cluster_resources(
            self.session, "", [resource_type], verify=verify
        )
        self.session.get.assert_called_once_with(
            f"api/v1/{resource_type}", verify=verify
        )
        self.resp.raise_for_status.assert_called_once()
        self.assertEqual(resources, {resource_type: self.data})

    def test_get_cluster_resources_success_custom_resource(self):
        """Ensure that custom resources can be retrieved."""
        self.resp.raise_for_status = MagicMock()
        self.session.get = MagicMock(return_value=self.resp)
        resource_type = "example.com/v1alpha1/mycustomtype"
        verify = True
        resources = get_cluster_resources(
            self.session, "", [resource_type], verify=verify
        )
        self.session.get.assert_called_once_with(f"apis/{resource_type}", verify=verify)
        self.resp.raise_for_status.assert_called_once()
        self.assertEqual(resources, {resource_type: self.data})

    def test_get_cluster_resources_not_found(self):
        """Ensure that function works for unfound resources."""
        self.resp.raise_for_status = MagicMock(side_effect=HTTPError())
        self.resp.status_code = 404
        self.session.get = MagicMock(return_value=self.resp)
        resource_types = ["r1"]
        verify = True
        resources = get_cluster_resources(
            self.session, "", resource_types, verify=verify
        )
        self.session.get.assert_called_once_with("api/v1/r1", verify=verify)
        self.resp.raise_for_status.assert_called_once()
        self.assertEqual(resources, {})

    def test_get_cluster_resources_server_error(self):
        """Ensure that function raises exception for non-404 responses."""
        self.resp.raise_for_status = MagicMock(side_effect=HTTPError())
        self.resp.status_code = 500
        self.session.get = MagicMock(return_value=self.resp)
        resource_types = ["r1"]
        verify = True
        with self.assertRaises(HTTPError):
            get_cluster_resources(self.session, "", resource_types, verify=verify)
