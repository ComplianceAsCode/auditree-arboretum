# -*- coding:utf-8; mode:python -*-
"""Organization repository forks evidence."""
import json

from compliance.evidence import RawEvidence


class OrgRepoForksEvidence(RawEvidence):
    """Organization repository forks evidence class."""

    @property
    def forks(self):
        """Provide organization repository forks as a list."""
        if self.content:
            f_factory = {
                'gh': self._get_gh_forks,
                'gl': self._get_gl_forks,
                'bb': self._get_bb_forks
            }
            if not hasattr(self, '_direct_collabs'):
                self._forks = f_factory[self.name[:2]]()
            return self._forks

    @property
    def as_a_list(self):
        """Provide forks content as a list."""
        if self.content:
            if not hasattr(self, '_as_a_list'):
                self._as_a_list = json.loads(self.content)
            return self._as_a_list

    def _get_gh_forks(self):
        repoforks = []
        for repo in self.as_a_list:
            forks = [f['html_url'] for f in self.as_a_list[repo]]
            if not forks:
                continue
            if forks:
                repoforks.append({'repo': repo, 'forks': forks})
        return repoforks

    def _get_gl_forks(self):
        raise NotImplementedError('Support for Gitlab coming soon...')

    def _get_bb_forks(self):
        raise NotImplementedError('Support for Bitbucket coming soon...')
