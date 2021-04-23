# -*- coding:utf-8; mode:python -*-
"""Organization direct collaborators evidence."""
import json

from compliance.evidence import RawEvidence


class OrgDirectCollaboratorsEvidence(RawEvidence):
    """Organization direct collaborators evidence class."""

    @property
    def direct_collabs(self):
        """Provide organization repository direct collaborators as a list."""
        if self.content:
            dc_factory = {
                'gh': self._get_gh_direct_collabs,
                'gl': self._get_gl_direct_collabs,
                'bb': self._get_bb_direct_collabs
            }
            if not hasattr(self, '_direct_collabs'):
                self._direct_collabs = dc_factory[self.name[:2]]()
            return self._direct_collabs

    @property
    def as_a_list(self):
        """Provide direct collaborators content as a list."""
        if self.content:
            if not hasattr(self, '_as_a_list'):
                self._as_a_list = json.loads(self.content)
            return self._as_a_list

    def _get_gh_direct_collabs(self):
        repocollabs = []
        for repo in self.as_a_list:
            collabs = []
            for c in self.as_a_list[repo]:
                collabs.append(c)
            if not collabs:
                continue
            if collabs:
                repocollabs.append({'repo': repo, 'collabs': collabs})
        return repocollabs

    def _get_gl_direct_collabs(self):
        raise NotImplementedError('Support for Gitlab coming soon...')

    def _get_bb_direct_collabs(self):
        raise NotImplementedError('Support for Bitbucket coming soon...')
