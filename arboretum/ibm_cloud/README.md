# IBM Cloud library

The fetchers and checks contained within this `ibm_cloud` category folder are
common tests that can be configured and executed for the purpose of generating
compliance reports and notifications using the [auditree-framework][].
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

### Cluster Resource

* Class: [ICClusterResourceFetcher][fetch-ibm-cloud-cluster-resource]
* Purpose: Write the resources of **managed** Kubernetes clusters to the evidence locker. NOTE: Do not use this fetcher for stand-alone clusters. For Kubernetes stand-alone clusters, use the [Kubernetes cluster resource fetcher][fetch-kube-cluster-resource].
* Behavior: Retrieve tokens for IBM Cloud Kubernetes clusters listed by [IBM Cloud cluster list fetcher][fetch-cluster-list] using `api_key` in `~/.credentials`, and then retrieve specified resources  using the tokens. TTL is set to 1 day.

* Configuration elements:
  * `org.ibm_cloud.accounts`
    * Required
    * List of accounts (string)
    * Each account is an arbitrary name describing the IBM Cloud account. It is used to match to the token provided in the
      credentials file in order for the fetcher to retrieve content from IBM Cloud for that account.
  * `org.ibm_cloud.cluster_resources.types`
    * Optional
    * List of resource types as strings
      * NOTE: For core group API resources, the resource name must be in
      _plural form_ (e.g., `secrets`).
      * NOTE: For other named group resources including custom API
        resources, the resource name must be in the following format:
        `APIGROUP/VERSION/NAME`. You can compose this by first executing
        `kubectl api-resources` and `kubectl api-versions` and then combining
        the results into your resource name.  Using `cronjobs` as an example:

        ```sh
        $ kubectl api-resources -o name | fgrep cronjobs
        cronjobs.batch
        $ kubectl api-versions | grep batch
        batch/v1
        batch/v1beta1
        ```

        For this example `batch/v1` is the more stable version so we use that
        to compose `APIGROUP/VERSION/NAME` resource name as `batch/v1/cronjobs`.
* Expected configuration:

  ```json
  {
    "org": {
      "ibm_cloud": {
        "accounts": [
          "myaccount1", "myaccount2"
        ],
        "cluster_resources": {
          "types": [
            "secrets", "batch/v1/cronjobs", "apigroup.example.com/v1/mycustom"
          ]
        }
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
   from arboretum.ibm_cloud.fetchers.fetch_cluster_resource import ICClusterResourceFetcher
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
[fetch-ibm-cloud-cluster-resource]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/ibm_cloud/fetchers/fetch_cluster_resource.py
[fetch-kube-cluster-resource]: https://github.com/ComplianceAsCode/auditree-arboretum/tree/main/arboretum/kubernetes#cluster-resource
