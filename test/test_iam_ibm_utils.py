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
"""Arboretum IBM Cloud IAM common utility module tests."""

import unittest
from unittest.mock import MagicMock, patch

from arboretum.common.iam_ibm_utils import get_tokens
from arboretum.common.ibm_constants import IAM_API_KEY_GRANT_TYPE

from requests import HTTPError


class IAMIBMTest(unittest.TestCase):
    """Arboretum IBM Cloud IAM common utility tests."""

    def setUp(self):
        """Initialize supporting test objects before each test."""
        self.post_patcher = patch("requests.post")
        self.mock_post = self.post_patcher.start()
        mock_resp = MagicMock()
        self.mock_raise_for_status = MagicMock()
        self.mock_json = MagicMock(
            return_value={"access_token": "foo", "refresh_token": "bar"}
        )
        mock_resp.raise_for_status = self.mock_raise_for_status
        mock_resp.json = self.mock_json
        self.mock_post.return_value = mock_resp

    def tearDown(self):
        """Clean up and house keeping after each test."""
        self.post_patcher.stop()

    def test_get_tokens_success(self):
        """Ensure tokens are returned as expected."""
        self.assertEqual(get_tokens("meh_api_key"), ("foo", "bar"))
        self.mock_post.assert_called_once_with(
            "https://iam.cloud.ibm.com/identity/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
            auth=("bx", "bx"),
            data=f"grant_type={IAM_API_KEY_GRANT_TYPE}&apikey=meh_api_key",
        )
        self.mock_raise_for_status.assert_called_once()
        self.mock_json.assert_called_once()

    def test_get_tokens_failure(self):
        """Ensure tokens are not returned and an error is raised."""
        self.mock_raise_for_status.side_effect = HTTPError("boom!")
        with self.assertRaises(HTTPError) as cm:
            self.assertIsNone(get_tokens("meh_api_key"))
            self.mock_post.assert_called_once_with(
                "https://iam.cloud.ibm.com/identity/token",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                },
                auth=("bx", "bx"),
                data=f"grant_type={IAM_API_KEY_GRANT_TYPE}&apikey=meh_api_key",
            )
            self.mock_raise_for_status.assert_called_once()
            self.mock_json.assert_not_called()
        self.assertEqual(str(cm.exception), "boom!")
