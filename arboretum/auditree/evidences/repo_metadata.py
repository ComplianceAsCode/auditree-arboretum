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
"""Repository metadata evidence."""

import json

from arboretum.common.constants import IGNORE_REPO_METADATA

from compliance.evidence import RawEvidence
from compliance.utils.data_parse import format_json


class RepoMetadataEvidence(RawEvidence):
    """Repository metadata raw evidence class."""

    @property
    def repo_size(self):
        """Provide the repo size."""
        if self.content:
            rs_factory = {
                'gh': self._get_gh_repo_size,
                'gl': self._get_gl_repo_size,
                'bb': self._get_bb_repo_size
            }
            if not hasattr(self, '_size'):
                self._size = rs_factory[self.name[:2]]()
            return self._size

    @property
    def filtered_content(self):
        """Provide evidence content minus the ignored fields as JSON."""
        if self.content:
            if not hasattr(self, '_filtered_content'):
                metadata = json.loads(self.content)
                for field in IGNORE_REPO_METADATA[self.name[:2]]:
                    try:
                        metadata.pop(field)
                    except KeyError:
                        pass
                self._filtered_content = str(format_json(metadata))
            return self._filtered_content

    def _get_gh_repo_size(self):
        return json.loads(self.content)['size']

    def _get_gl_repo_size(self):
        raise NotImplementedError('Support for Gitlab coming soon...')

    def _get_bb_repo_size(self):
        raise NotImplementedError('Support for Bitbucket coming soon...')
