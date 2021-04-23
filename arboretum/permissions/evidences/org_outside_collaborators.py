# -*- coding:utf-8; mode:python -*-
"""Organization outside collaborators evidence."""
import json

from compliance.evidence import RawEvidence


class OrgOutSideCollaboratorsEvidence(RawEvidence):
    """Organization outside collaborators evidence class."""

    @property
    def outside_collabs(self):
        """Provide organization repository outside collaborators as a list."""
        if self.content:
            dc_factory = {
                'gh': self._get_gh_outside_collabs,
                'gl': self._get_gl_outside_collabs,
                'bb': self._get_bb_outside_collabs
            }
            if not hasattr(self, '_outside_collabs'):
                self._outside_collabs = dc_factory[self.name[:2]]()
            return self._outside_collabs

    @property
    def as_a_list(self):
        """Provide outside collaborators content as a list."""
        if self.content:
            if not hasattr(self, '_as_a_list'):
                self._as_a_list = json.loads(self.content)
            return self._as_a_list

    def _get_gh_outside_collabs(self):
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

    def _get_gl_outside_collabs(self):
        raise NotImplementedError('Support for Gitlab coming soon...')

    def _get_bb_outside_collabs(self):
        raise NotImplementedError('Support for Bitbucket coming soon...')
