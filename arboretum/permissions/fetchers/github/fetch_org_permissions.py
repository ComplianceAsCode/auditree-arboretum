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
"""Github organization permissions fetcher."""
import json

import arboretum.permissions.fetchers.github.fetch_org_collaborators as collabs


class GithubOrgPermissionsFetcher(collabs.GithubOrgCollaboratorsFetcher):
    """Fetch Github permissions evidence."""

    def fetch_repo_forks(self):
        """Fetch Github repository forks."""
        for config in self.config.get("org.permissions.org_integrity.orgs"):
            host, org = config["url"].rsplit("/", 1)
            url_hash = collabs.get_sha256_hash([config["url"]], 10)
            path = ["permissions", f"gh_forks_{url_hash}.json"]
            description = f"Forks of repos in the {org} GH org"
            self.config.add_evidences(
                [collabs.RawEvidence(path[1], path[0], collabs.DAY, description)]
            )
            with collabs.raw_evidence(self.locker, "/".join(path)) as evidence:
                if evidence:
                    if host not in self.gh_pool:
                        self.gh_pool[host] = collabs.Github(base_url=host)
                    if not config.get("repos"):
                        repos = self.gh_pool[host].paginate_api(f"orgs/{org}/repos")
                        config["repos"] = [repo["name"] for repo in repos]
                    forks = {}
                    for repo in config["repos"]:
                        forks[repo] = self.gh_pool[host].paginate_api(
                            f"repos/{org}/{repo}/forks"
                        )
                    evidence.set_content(json.dumps(forks))

    def fetch_repo_teams(self):
        """Fetch Github repository teams."""
        for config in self.config.get("org.permissions.org_integrity.orgs"):
            host, org = config["url"].rsplit("/", 1)
            url_hash = collabs.get_sha256_hash([config["url"]], 10)
            path = ["permissions", f"gh_teams_{url_hash}.json"]
            description = f"Repo access for GH teams in the {org} GH org"
            self.config.add_evidences(
                [collabs.RawEvidence(path[1], path[0], collabs.DAY, description)]
            )
            with collabs.raw_evidence(self.locker, "/".join(path)) as evidence:
                if evidence:
                    if host not in self.gh_pool:
                        self.gh_pool[host] = collabs.Github(base_url=host)
                    if not config.get("repos"):
                        repos = self.gh_pool[host].paginate_api(f"orgs/{org}/repos")
                        config["repos"] = [repo["name"] for repo in repos]
                    teams = {}
                    for repo in config["repos"]:
                        teams[repo] = self.gh_pool[host].paginate_api(
                            f"repos/{org}/{repo}/teams"
                        )
                    evidence.set_content(json.dumps(teams))
