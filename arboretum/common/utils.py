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
"""Common utility functions."""

from compliance.evidence import DAY, HOUR


def parse_seconds(seconds):
    """
    Parse seconds (int) into a human readable string.

    :returns: "D days, H hours, M minutes, S seconds" string
    """
    intervals = [("days", DAY), ("hours", HOUR), ("minutes", 60), ("seconds", 1)]
    formatted = []
    for interval in intervals:
        q, r = divmod(seconds, interval[1])
        if q:
            unit = interval[0][:-1] if q == 1 else interval[0]
            formatted.append(f"{q} {unit}")
        seconds = r
    return ", ".join(formatted)
