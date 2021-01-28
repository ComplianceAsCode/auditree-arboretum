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
"""
The compliance OSCAL observations report.

A json report comprising NIST OSCAL Assessment Results Observations generated
by processing compliance operator fetcher cluster_resource evidence. The
embedded XML within the cluster_resource evidence is transformed to produce the
report. If an optional oscal_metadata file is specified, then the report is
enhanced accordingly.

Provide the "start" and "end" optional configuration (--config) parameters
as a JSON string, in "YYYYMMDD" format to define a date range for the evidence
used to process the report.  If omitted, the default value is the current date.

---------------
Example usages:
---------------

> harvest report my-repo arboretum compliance_oscal_observations

> harvest report my-repo arboretum compliance_oscal_observations \
--config '{ \
"oscal_metadata":"raw/kubernetes/oscal_metadata.yaml" \
}'

> harvest report my-repo arboretum compliance_oscal_observations \
--config '{ \
"cluster_resource":"raw/kubernetes/cluster_resource.json", \
"oscal_metadata":"raw/kubernetes/oscal_metadata.yaml", \
"start":"20200901", \
"end":"20201231" \
}'

--------------------
oscal_metadata.yaml:
--------------------

The oscal_metadata.yaml file comprises one or more mappings. Below is shown the
format of a single mapping. The items in angle brackets are to be replaced with
desired values for augmenting the produced OSCAL.

The mapping whose <name> matches the [metadata][name] in the evidence for the
corresponding embedded XML, if any, is used for augmenting the produced OSCAL.

<name>:
   namespace: <namespace>
   subject-references:
      component:
         uuid-ref: <uuid-ref-component>
         type: <component-type>
         title: <component-title>
      inventory-item:
         uuid-ref: <uuid-ref-inventory-item>
         type: <inventory-item-type>
         title: <inventory-item-title>
         properties:
            target: <target>
            cluster-name: <cluster-name>
            cluster-type: <cluster-type>
            cluster-region: <cluster-region>

A sample oscal_metadata.yaml file with 2 mappings is shown below.

ssg-ocp4-ds-cis-111.222.333.444-pod:
   namespace: xccdf
   subject-references:
      component:
         uuid-ref: 56666738-0f9a-4e38-9aac-c0fad00a5821
         type: component
         title: Red Hat OpenShift Kubernetes
      inventory-item:
         uuid-ref: 46aADFAC-A1fd-4Cf0-a6aA-d1AfAb3e0d3e
         type: inventory-item
         title: Pod
         properties:
            target: kube-br7qsa3d0vceu2so1a90-roksopensca-0000026b.iks.mycorp
            cluster-name: ROKS-OpenSCAP-1
            cluster-type: openshift
            cluster-region: us-south
ssg-rhel7-ds-cis-111.222.333.444-pod:
   namespace: xccdf
   subject-references:
      component:
         uuid-ref: 89cfe7a7-ce6b-4699-aa7b-2f5739c72001
         type: component
         title: RedHat Enterprise Linux 7.8
      inventory-item:
         uuid-ref: 46aADFAC-A1fd-4Cf0-a6aA-d1AfAb3e0d3e
         type: inventory-item
         title: VM
         properties:
            target: kube-br7qsa3d0vceu2so1a90-roksopensca-0000026b.iks.mycorp
            cluster-name: ROKS-OpenSCAP-1
            cluster-type: openshift
            cluster-region: us-south
"""

import json
from datetime import datetime, timedelta

from harvest.reporter import BaseReporter

from trestle.utils import osco

import yaml


class ComplianceOscalObservations(BaseReporter):
    """The compliance oscal observations class."""

    @property
    def report_filename(self):
        """Return the report filename."""
        return 'compliance_oscal_observations.json'

    def generate_report(self):
        """
        Generate the compliance oscal observations report content.

        :returns: stringified OSCAL json content
        """
        # get required cluster resource path
        path_cluster_resource = self.config.get(
            'cluster_resource', 'raw/kubernetes/cluster_resource.json'
        )
        # get optional oscal_metadata path
        path_oscal_metadata = self.config.get(
            'oscal_metadata', 'raw/kubernetes/oscal_metadata.yaml'
        )
        # get start+end dates
        start_dt = datetime.strptime(
            self.config.get('start', datetime.today().strftime('%Y%m%d')),
            '%Y%m%d'
        )
        end_dt = datetime.strptime(
            self.config.get('end', datetime.today().strftime('%Y%m%d')),
            '%Y%m%d'
        )
        if start_dt > end_dt:
            raise ValueError('Cannot have start date before end date.')
        current_dt = start_dt
        previous = None
        observation_list = []
        # examine each day's evidence, if any
        while current_dt <= end_dt:
            try:
                cluster_resource = json.loads(
                    self.get_file_content(path_cluster_resource, current_dt)
                )
                try:
                    oscal_metadata = yaml.load(
                        self.get_file_content(path_oscal_metadata, current_dt),
                        Loader=yaml.FullLoader
                    )
                    # add locker info to oscal metadata
                    for key in oscal_metadata.keys():
                        entry = oscal_metadata[key]
                        entry['locker'] = self.repo_url
                except Exception:
                    oscal_metadata = None
                # skip if no new evidence
                if previous != cluster_resource:
                    previous = cluster_resource
                    # examine entries skipping those not relevant
                    for key in cluster_resource.keys():
                        for group in cluster_resource[key]:
                            for cluster in cluster_resource[key][group]:
                                for resource in cluster.get('resources', []):
                                    self._update_observations(
                                        observation_list,
                                        resource,
                                        oscal_metadata
                                    )
            except Exception:
                pass
            current_dt = current_dt + timedelta(days=1)
        # create report
        if len(observation_list) == 0:
            raise RuntimeError('No report content.')
        observation_dict = json.dumps(
            {'observations': observation_list}, indent=2
        )
        report = str(observation_dict)
        return report

    def _update_observations(self, observation_list, resource, oscal_metadata):
        """Update observations list with additional observations."""
        if resource.get('kind') != 'ConfigMap':
            return
        if 'data' not in resource.keys():
            return
        if 'results' not in resource['data'].keys():
            return
        if 'metadata' not in resource.keys():
            return
        if 'name' not in resource['metadata'].keys():
            return
        # assemble osco data for transformation
        data = {'results': resource['data']['results']}
        osco_data = {
            'kind': resource['kind'],
            'data': data,
            'metadata': resource['metadata']
        }
        # get OSCAL Observation objects
        arp, analysis = osco.get_observations(osco_data, oscal_metadata)
        # convert Observation objects into json
        for observation_model in arp.observations:
            observation_json = json.loads(
                observation_model.json(
                    exclude_none=True, by_alias=True, indent=2
                )
            )
            observation_list.append(observation_json)
