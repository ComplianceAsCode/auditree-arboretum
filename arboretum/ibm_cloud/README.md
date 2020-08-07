# IBM Cloud library

The fetchers and checks contained within this `ibm_cloud` category folder are
common tests that can be configured and executed for the purpose of generating
compliance reports and notifications using the [auditree-framework][].  They
validate the configuration and ensure smooth execution of an auditree instance.
See [auditree-framework documentation][] for more details.

These tests are normally executed by a CI/CD system like
[Travis CI](https://travis-ci.com/) as part of another project that uses this
library package as a dependency.

## Usage as a library

See [usage][] for specifics on including this library as a dependency and how
to include the fetchers and checks from this library in your downstream project.

## Fetchers

### Cluster List

* Class: [ClusterListFetcher][fetch-cluster-list]
* Purpose: Write the list of IBM Cloud clusters to the evidence locker.
* Behavior: Access [IBM Cloud API][ibm-cloud-api] and save the list of clusters bound with specified account.
* Configuration elements:
  * `org.ibm_cloud.accounts`
    * Required
    * List of accounts (string)
    * Each account is an arbitrary name describing the IBM Cloud account. It is used to match to the token provided in the
      credentials file in order for the fetcher to retrieve content from IBM Cloud for that account.
* Example (required) configuration:

  ```json
  {
    "org": {
      "ibm_cloud": {
        "accounts": ["myaccount1"]
      }
    }
  }
  ```

* Required credentials:
  * `ibm_cloud` credentials with read/view permissions are needed for this fetcher to successfully retrieve the evidence.
    * `XXX_api_key`: API key string for account `XXX`.
    * Example credential file entry:

      ```ini
      [ibm_cloud]
      acct_a_api_key=your-ibm-cloud-api-key-for-acct-a
      acct_b_api_key=your-ibm-cloud-api-key-for-acct-b
      ```

    * NOTE: API keys can be generated using the [IBM Cloud CLI][ic-api-key-create] or [IBM Cloud Console][ibm-cloud-gen-api-console]. Example to create an API key with IBM Cloud CLI is:

      ```sh
      ibmcloud iam api-key-create your-iks-api-key-for-acct-x
      ```

* Import statement:

   ```python
   from arboretum.ibm_cloud.fetchers.fetch_cluster_list import ClusterListFetcher
   ```

## Checks

Checks coming soon...

[auditree-framework]: https://github.com/ComplianceAsCode/auditree-framework
[auditree-framework documentation]: https://complianceascode.github.io/auditree-framework/
[usage]: https://github.com/ComplianceAsCode/auditree-arboretum#usage
[ic-api-key-create]: https://cloud.ibm.com/docs/cli/reference/ibmcloud?topic=cloud-cli-ibmcloud_commands_iam#ibmcloud_iam_api_key_create
[fetch-cluster-list]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/ibm_cloud/fetchers/fetch_cluster_list.py
[ibm-cloud-api]: https://containers.cloud.ibm.com/
[ibm-cloud-gen-api-console]: https://cloud.ibm.com/docs/account?topic=account-userapikey#create_user_key