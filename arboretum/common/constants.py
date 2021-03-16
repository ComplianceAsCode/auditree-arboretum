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
"""Common constants."""

# PyPI RSS feed base URL
PYPI_RSS_BASE_URL = 'https://pypi.org/rss/project'

# Repository metadata fields to ignore.  Used for repo integrity.
IGNORE_REPO_METADATA = {
    'gh': [
        'pushed_at',
        'size',
        'updated_at',
        'stargazers_count',
        'subscribers_count',
        'watchers',
        'watchers_count',
        'open_issues',
        'open_issues_count',
        'temp_clone_token'
    ]
}

# Evidence locker metadata datetime format
LOCKER_DTTM_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

# Github host URL
GH_HOST_URL = 'https://github.com'

# Zenhub public API
ZH_API_ROOT = 'https://api.zenhub.com'

# Default affiliation type to fetch github repo collaborators
GH_ALL_COLLABORATORS = ['all']
