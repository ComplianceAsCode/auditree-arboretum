"""Utility function for IBM Cloud IAM."""
import requests


def get_tokens(api_key):
    """Get tokens (access token and refresh token) by api_key.

    see https://cloud.ibm.com/apidocs/iam-identity-token-api
    """
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    resp = requests.post(
        'https://iam.cloud.ibm.com/identity/token',
        headers=headers,
        auth=('bx', 'bx'),
        data='grant_type=urn:ibm:params:oauth:grant-type:'
        f'apikey&apikey={api_key}'
    )
    resp.raise_for_status()
    return resp.json()
