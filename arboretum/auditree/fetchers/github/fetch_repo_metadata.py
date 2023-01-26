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
"""Github repository metadata fetcher."""

import json
import os
from urllib.parse import urlparse

from arboretum.auditree.evidences.repo_metadata import RepoMetadataEvidence

from compliance.evidence import DAY, raw_evidence
from compliance.fetch import ComplianceFetcher
from compliance.utils.services.github import Github


class GithubRepoMetaDataFetcher(ComplianceFetcher):
    """Fetch Github repository metadata."""

    def fetch_gh_repo_details(self):
        """Fetch Github repository metadata."""
        repo_urls = self.config.get(
            "org.auditree.repo_integrity.repos", [self.config.get("locker.repo_url")]
        )
        current_url = None
        github = None
        for repo_url in repo_urls:
            parsed = urlparse(repo_url)
            base_url = f"{parsed.scheme}://{parsed.hostname}"
            repo = parsed.path.strip("/")
            file_prefix = repo.lower().replace("/", "_").replace("-", "_")
            path = ["auditree", f"gh_{file_prefix}_repo_metadata.json"]
            if base_url != current_url:
                github = Github(self.config.creds, base_url)
                current_url = base_url
            self.config.add_evidences(
                [
                    RepoMetadataEvidence(
                        path[1], path[0], DAY, f"Github {repo} repo metadata details"
                    )
                ]
            )
            with raw_evidence(self.locker, os.path.join(*path)) as evidence:
                if evidence:
                    evidence.set_content(json.dumps(github.get_repo_details(repo)))
