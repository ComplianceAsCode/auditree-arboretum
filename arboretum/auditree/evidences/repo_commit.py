# -*- mode:python; coding:utf-8 -*-
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
"""Repository commit evidence."""

import json

from compliance.evidence import RawEvidence


class RepoCommitEvidence(RawEvidence):
    """Repository commit raw evidence class."""

    @property
    def commit_signed_status(self):
        """Provide verified/signed status for each commit as a list."""
        if self.content:
            rs_factory = {
                'gh': self._get_gh_commit_signed_status,
                'gl': self._get_gl_commit_signed_status,
                'bb': self._get_bb_commit_signed_status
            }
            if not hasattr(self, '_commit_signed_status'):
                self._commit_signed_status = rs_factory[self.name[:2]]()
            return self._commit_signed_status

    def _get_gh_commit_signed_status(self):
        commits = []
        for commit in json.loads(self.content):
            commits.append(
                {
                    'sha': commit['sha'],
                    'url': commit['html_url'],
                    'signed': commit['commit']['verification']['verified']
                }
            )
        return commits

    def _get_gl_commit_signed_status(self):
        raise NotImplementedError('Support for Gitlab coming soon...')

    def _get_bb_commit_signed_status(self):
        raise NotImplementedError('Support for Bitbucket coming soon...')
