# Copyright (c) 2023 EnterpriseDB Corp. All rights reserved.
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
"""Common utils."""

import requests

from collections import defaultdict
from compliance.config import get_config


def get_token(
    client_id,
    client_secret,
    tenant_id,
    grant_type="client_credentials",
    scope="https://management.azure.com/.default",
):
    """Get Azure Cloud access token. returns: the access token."""
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    data = (
        f"grant_type={grant_type}&client_id={client_id}"
        + f"&client_secret={client_secret}&scope={scope}"
    )
    resp = requests.post(url, headers=headers, data=data)
    resp.raise_for_status()
    token = resp.json()
    return token["access_token"]


def get_credentials(config, account):
    """Get credential for the account."""
    client_id = config.creds.get("azure_cloud", key="clientid", account=account)
    client_secret = config.creds.get("azure_cloud", key="clientsecret", account=account)
    tenant_id = config.creds.get("azure_cloud", key="tenantid", account=account)
    subscription_id = config.creds.get(
        "azure_cloud", key="subscriptionid", account=account
    )

    return client_id, client_secret, tenant_id, subscription_id


def get_assessments_by_account(account, session, config, api):
    """
    Call the get_assessments generator for each configured account.

    Build up a dict of results.
    """
    assessments = defaultdict(list)
    for assessments_resp in paginate_api(account, session, config, api):
        assessments[account].extend(assessments_resp.get("value", []))
    return assessments


def paginate_api(account, session, config, api_url):
    """
    Call the API until there's no longer a nextLink.

    Yeilding data as we go.
    """
    client_id, client_secret, tenant_id, _ = get_credentials(config, account)
    token = get_token(client_id, client_secret, tenant_id)
    session.headers.update({"Authorization": f"Bearer {token}"})
    while api_url:
        # get credential for the account
        response = session.get(api_url)
        response.raise_for_status()
        data = response.json()
        api_url = data.get("nextLink")
        yield data


def get_azure_accounts():
    return get_config().get("org.azure_cloud.accounts")
