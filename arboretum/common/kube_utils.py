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
"""Common Kubernetes functions."""

import re

from requests import HTTPError


def get_cluster_resources(session, token, resource_types, verify=True):
    """Get resource from cluster.

    :param requests.Session session: a requests.session object
    :param str token: Bearer token
    :param list resource_types: list of resource types. Valid values can
      be pluralized resource types like "nodes" and "pods" or custom
      resource API names such as "apigroup.example.com/v1/mycustom".
    :param verify: path to a CA certificate, or True/False. Set to False to
      skip TLS server certificate verification.  Defaults to True.
    """
    session.headers.update({"Authorization": f"Bearer {token}"})
    resources = {}
    for resource_type in resource_types:
        resource_is_named_group = re.match(r"[^/]+/[^/]+/[^/]+", resource_type)
        base_url = "apis" if resource_is_named_group else "api/v1"
        try:
            resp = session.get(f"{base_url}/{resource_type}", verify=verify)
            resp.raise_for_status()
            resources[resource_type] = resp.json()["items"]
        except HTTPError:
            if resp.status_code != 404:
                raise
            continue
    return resources
