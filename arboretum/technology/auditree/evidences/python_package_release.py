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
"""Python PyPI release evidence."""

from xml.etree.ElementTree import fromstring

from compliance.evidence import RawEvidence


class PackageReleaseEvidence(RawEvidence):
    """Python package release raw evidence class."""

    @property
    def latest_release(self):
        """
        Get the latest release from the evidence.

        Gets the latest release version for the Python package represented
        by the evidence.
        """
        if not self.content:
            return
        if not hasattr(self, '_latest_release'):
            root = fromstring(self.content)
            self._latest_release = root[0].find('item').find('title').text
        return self._latest_release
