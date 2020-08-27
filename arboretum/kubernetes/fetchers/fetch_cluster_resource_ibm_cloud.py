"""Feching cluster resouce from IBM Cloud."""

import io
import json
import os
import pathlib
import tempfile
import zipfile

from compliance.evidence import evidences

import requests

import yaml

from ...ibm_cloud.util.iam import get_tokens


def fetch_cluster_resource(parent):
    """Feching cluster resouce from IBM Cloud."""
    resource_types = parent.config.get(
        'org.ibm_cloud.cluster_resource.target_resource_types',
        parent.RESOURCE_TYPE_DEFAULT
    )
    cluster_list = {}
    with evidences(parent.locker, 'raw/ibm_cloud/cluster_list.json') as ev:
        cluster_list = json.loads(ev.content)

    resources = {}
    for account in cluster_list:
        api_key = getattr(
            parent.config.creds['ibm_cloud'], f'{account}_api_key'
        )

        tokens = get_tokens(api_key)
        resources[account] = []
        for cluster in cluster_list[account]:
            try:
                if cluster['type'] == 'kubernetes':
                    # get token for an IKS cluster
                    # https://cloud.ibm.com/apidocs/kubernetes#getclusterconfig
                    headers = {
                        'Authorization': 'Bearer '
                        f'{tokens["access_token"]}',
                        'X-Auth-Refresh-Token': tokens['refresh_token']
                    }
                    resp = requests.get(
                        'https://containers.cloud.ibm.com'
                        '/global/v1/clusters/'
                        f'{cluster["id"]}/config',
                        headers=headers
                    )
                    resp.raise_for_status()
                    z = zipfile.ZipFile(io.BytesIO(resp.content))
                    cluster_token = None
                    ca_cert_filepath = None
                    for name in z.namelist():
                        p = pathlib.Path(name)
                        if p.name.startswith('kube-config'):
                            kubeconfig = yaml.safe_load(z.read(name))
                            cluster_token = kubeconfig['users'][0]['user'][
                                'auth-provider']['config']['id-token']
                        if p.name.endswith('.pem'):
                            tmpdir = tempfile.TemporaryDirectory()
                            z.extract(name, path=tmpdir.name)
                            ca_cert_filepath = os.path.join(tmpdir.name, name)
                    if cluster_token is None:
                        parent.logger.error(
                            'Failed to extract token from the config file '
                            'for cluster "%s".',
                            cluster['name']
                        )
                        continue
                    if ca_cert_filepath is None:
                        parent.logger.error(
                            'Failed to extract CA certificate file (*.pem)'
                            ' from the config file'
                            ' for cluster "%s".',
                            cluster['name']
                        )
                        continue
                    headers = {'Authorization': f'Bearer {cluster_token}'}
                    cluster['resources'] = {}
                    for resource in resource_types:
                        resp = requests.get(
                            f'{cluster["serverURL"]}/api/v1/{resource}s',
                            headers=headers,
                            verify=ca_cert_filepath
                        )
                        resp.raise_for_status()
                        cluster['resources'][resource] = resp.json()['items']
                elif cluster['type'] == 'openshift':
                    parent.logger.warning(
                        'Not implemented cluster type %s: %s',
                        cluster['type'],
                        cluster['name']
                    )
                else:
                    parent.logger.warning(
                        'Ignoring unsupported cluster type "%s": %s',
                        cluster['type'],
                        cluster['name']
                    )
                resources[account].append(cluster)
            except Exception as e:
                parent.logger.error(
                    'Failed to get resource from cluster "%s": %s',
                    cluster['name'],
                    str(e)
                )

    return resources
