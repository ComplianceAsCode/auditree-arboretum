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
"""Github organization collaborators fetcher."""

import json

from arboretum.common.constants import GH_ALL_COLLABORATORS

from compliance.evidence import DAY, RawEvidence, raw_evidence
from compliance.fetch import ComplianceFetcher
from compliance.utils.data_parse import get_sha256_hash
from compliance.utils.services.github import Github


class GithubOrgCollaboratorsFetcher(ComplianceFetcher):
    """Fetch collaborators from GH organization repositories."""

    @classmethod
    def setUpClass(cls):
        """Initialize the fetcher object with configuration settings."""
        cls.gh_pool = {}
        return cls

    def fetch_gh_org_collaborators(self):
        """Fetch collaborators from GH organization repositories."""
        for config in self.config.get("org.permissions.org_integrity.orgs"):
            host, org = config["url"].rsplit("/", 1)
            for aff in config.get("collaborator_types", GH_ALL_COLLABORATORS):
                url_hash = get_sha256_hash([config["url"]], 10)
                json_file = f"gh_{aff}_collaborators_{url_hash}.json"
                path = ["permissions", json_file]
                description = f"{aff.title()} collaborators of the {org} GH org"
                self.config.add_evidences(
                    [RawEvidence(path[1], path[0], DAY, description)]
                )
                with raw_evidence(self.locker, "/".join(path)) as evidence:
                    if evidence:
                        if host not in self.gh_pool:
                            self.gh_pool[host] = Github(base_url=host)
                        if not config.get("repos"):
                            repos = self.gh_pool[host].paginate_api(f"orgs/{org}/repos")
                            config["repos"] = [repo["name"] for repo in repos]
                        collabs = {}
                        for repo in config["repos"]:
                            collabs_url = f"repos/{org}/{repo}/collaborators"
                            collabs[repo] = self.gh_pool[host].paginate_api(
                                collabs_url, affiliation=aff
                            )
                        evidence.set_content(json.dumps(collabs))
