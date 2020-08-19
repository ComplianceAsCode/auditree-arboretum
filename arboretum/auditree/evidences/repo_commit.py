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
    def signed_status(self):
        """Provide verified/signed status for each commit as a list."""
        if self.content:
            ss_factory = {
                'gh': self._get_gh_signed_status,
                'gl': self._get_gl_signed_status,
                'bb': self._get_bb_signed_status
            }
            if not hasattr(self, '_signed_status'):
                self._signed_status = ss_factory[self.name[:2]]()
            return self._signed_status

    @property
    def author_info(self):
        """Provide author name and date/time for each commit as a list."""
        if self.content:
            ai_factory = {
                'gh': self._get_gh_author_info,
                'gl': self._get_gl_author_info,
                'bb': self._get_bb_author_info
            }
            if not hasattr(self, '_author_info'):
                self._author_info = ai_factory[self.name[:2]]()
            return self._author_info

    @property
    def as_a_list(self):
        """Provide recent commits content as a list."""
        if self.content:
            if not hasattr(self, '_as_a_list'):
                self._as_a_list = json.loads(self.content)
            return self._as_a_list

    def _get_gh_signed_status(self):
        commits = []
        for commit in self.as_a_list:
            commits.append(
                {
                    'sha': commit['sha'],
                    'url': commit['html_url'],
                    'signed': commit['commit']['verification']['verified']
                }
            )
        return commits

    def _get_gl_signed_status(self):
        raise NotImplementedError('Support for Gitlab coming soon...')

    def _get_bb_signed_status(self):
        raise NotImplementedError('Support for Bitbucket coming soon...')

    def _get_gh_author_info(self):
        commits = []
        for commit in self.as_a_list:
            commits.append(
                {
                    'sha': commit['sha'],
                    'url': commit['html_url'],
                    'author': commit['commit']['author']['name'],
                    'datetime': commit['commit']['author']['date']
                }
            )
        return commits

    def _get_gl_author_info(self):
        raise NotImplementedError('Support for Gitlab coming soon...')

    def _get_bb_author_info(self):
        raise NotImplementedError('Support for Bitbucket coming soon...')
