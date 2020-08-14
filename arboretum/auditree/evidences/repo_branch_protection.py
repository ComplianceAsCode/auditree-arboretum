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
"""Repository branch protection evidence."""

import json

from compliance.evidence import RawEvidence


class RepoBranchProtectionEvidence(RawEvidence):
    """Repository branch protection raw evidence class."""

    @property
    def admin_enforce(self):
        """Provide branch protection status for admins as a property."""
        if self.content:
            ae_factory = {
                'gh': self._get_gh_admin_enforce,
                'gl': self._get_gl_admin_enforce,
                'bb': self._get_bb_admin_enforce
            }
            if not hasattr(self, '_admin_enforce'):
                self._admin_enforce = ae_factory[self.name[:2]]()
            return self._admin_enforce

    def _get_gh_admin_enforce(self):
        as_dict = json.loads(self.content)
        return as_dict.get('enforce_admins', {}).get('enabled', False)

    def _get_gl_admin_enforce(self):
        raise NotImplementedError('Support for Gitlab coming soon...')

    def _get_bb_admin_enforce(self):
        raise NotImplementedError('Support for Bitbucket coming soon...')
