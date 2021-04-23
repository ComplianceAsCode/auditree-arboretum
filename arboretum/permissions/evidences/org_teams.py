# -*- coding:utf-8; mode:python -*-
"""Organization repository teams evidence."""
import json

from compliance.evidence import RawEvidence


class OrgTeamsEvidence(RawEvidence):
    """Organization repository teams evidence class."""

    @property
    def teams(self):
        """Provide organization repository teams as a list."""
        if self.content:
            t_factory = {
                'gh': self._get_gh_teams,
                'gl': self._get_gl_teams,
                'bb': self._get_bb_teams
            }
            if not hasattr(self, '_direct_collabs'):
                self._teams = t_factory[self.name[:2]]()
            return self._teams

    @property
    def as_a_list(self):
        """Provide teams content as a list."""
        if self.content:
            if not hasattr(self, '_as_a_list'):
                self._as_a_list = json.loads(self.content)
            return self._as_a_list

    def _get_gh_teams(self):
        repoteams = []
        for repo in self.as_a_list:
            teams = [t['name'] for t in self.as_a_list[repo]]
            if not teams:
                continue
            if teams:
                repoteams.append({'repo': repo, 'teams': teams})
        return repoteams

    def _get_gl_teams(self):
        raise NotImplementedError('Support for Gitlab coming soon...')

    def _get_bb_teams(self):
        raise NotImplementedError('Support for Bitbucket coming soon...')
