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
"""Utility module for IBM Cloud IAM."""

from arboretum.common.ibm_constants import IAM_API_KEY_GRANT_TYPE, IAM_TOKEN_URL

import requests


def get_tokens(api_key):
    """
    Get IBM Cloud access token and refresh token based on api_key.

    See: https://cloud.ibm.com/apidocs/iam-identity-token-api

    :param str api_key: the IBM Cloud API key for an IBM Cloud account

    :returns: a tuple containing the access token and the refresh token
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    resp = requests.post(
        IAM_TOKEN_URL,
        headers=headers,
        auth=("bx", "bx"),
        data=f"grant_type={IAM_API_KEY_GRANT_TYPE}&apikey={api_key}",
    )
    resp.raise_for_status()
    tokens = resp.json()
    return tokens["access_token"], tokens["refresh_token"]
