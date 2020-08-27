"""Feching cluster resouce from IBM Cloud."""

import io
import json
import os
import pathlib
import tempfile
import zipfile

from arboretum.common.iam_ibm import get_tokens

from compliance.evidence import evidences

import requests

import yaml


def fetch_cluster_resource(parent):
    """Feching cluster resouce from IBM Cloud."""
    resource_types = parent.config.get(
        'org.ibm_cloud.cluster_resource.target_resource_types',
        parent.RESOURCE_TYPE_DEFAULT
    )

    headers = {'Accept': 'application/json'}
    parent.session('https://containers.cloud.ibm.com', **headers)

    cluster_list = {}
    with evidences(parent.locker, 'raw/ibm_cloud/cluster_list.json') as ev:
        cluster_list = json.loads(ev.content)

    resources = {}
    for account in cluster_list:
        api_key = getattr(
            parent.config.creds['ibm_cloud'], f'{account}_api_key'
        )

        tokens = get_tokens(api_key)
        parent.session().headers.update(
            {
                'Authorization': 'Bearer '
                f'{tokens["access_token"]}',
                'X-Auth-Refresh-Token': tokens['refresh_token']
            }
        )

        # bulk retrieve config
        cluster_config = {}
        for cluster in cluster_list[account]:
            # get token for an IKS cluster
            # https://cloud.ibm.com/apidocs/kubernetes#getclusterconfig
            resp = parent.session().get(
                '/global/v1/clusters/'
                f'{cluster["id"]}/config'
            )
            resp.raise_for_status()
            cluster_config[cluster['name']] = zipfile.ZipFile(
                io.BytesIO(resp.content)
            )

        # bulk retrieve resource
        resources[account] = []
        for cluster in cluster_list[account]:
            s = requests.session()  # session for cluster
            try:
                z = cluster_config[cluster['name']]
                cluster_token = None
                ca_cert_filepath = None
                if cluster['type'] == 'kubernetes':
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
                elif cluster['type'] == 'openshift':
                    # https://cloud.ibm.com/docs/openshift?topic=openshift-access_cluster
                    url = (
                        f'{cluster["serverURL"]}/.well-known/'
                        'oauth-authorization-server'
                    )
                    resp = s.get(url)
                    resp.raise_for_status()
                    token_endpoint = resp.json()['token_endpoint']
                    parent.logger.debug('token_endpoint: %s', token_endpoint)
                    oauth_server = token_endpoint.split('/')[2]
                    headers = {'X-CSRF-Token': 'a'}
                    url = (
                        f'https://{oauth_server}/oauth/authorize?client_id='
                        'openshift-challenging-client&response_type=token'
                    )
                    parent.logger.debug(
                        'Getting access token from oauth server %s', url
                    )
                    resp = requests.get(
                        url,
                        auth=('apikey', api_key),
                        headers=headers,
                        allow_redirects=False
                    )
                    # do not log resp.header because it contains
                    # token string.
                    location = resp.headers['Location']
                    keyword = 'access_token='
                    start = location.find(keyword)
                    end = location.find('&', start)
                    cluster_token = location[start + len(keyword):end]
                    s.headers.update({'X-CSRF-Token': None})
                else:
                    parent.logger.warning(
                        'Ignoring unsupported cluster type "%s": %s',
                        cluster['type'],
                        cluster['name']
                    )
                    continue
                headers = {'Authorization': f'Bearer {cluster_token}'}
                s.headers.update(headers)
                try:
                    cluster['resources'] = {}
                    for resource in resource_types:
                        resp = s.get(
                            f'{cluster["serverURL"]}/api/v1/{resource}',
                            verify=ca_cert_filepath
                        )
                        resp.raise_for_status()
                        cluster['resources'][resource] = resp.json()['items']
                finally:
                    s.close()

                resources[account].append(cluster)
            except Exception as e:
                parent.logger.error(
                    'Failed to get resource from cluster "%s": %s',
                    cluster['name'],
                    str(e)
                )
                raise

    return resources
