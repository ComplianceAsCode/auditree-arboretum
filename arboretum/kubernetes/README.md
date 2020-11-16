# Kubernetes library

The fetchers and checks contained within this `kubernetes` category folder are
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

### Cluster Resource

* Class: [ClusterResourceFetcher][fetch-cluster-resource]
* Purpose: Write the resources of **stand-alone** Kubernetes clusters to the
evidence locker.  **NOTE:** Do not use this fetcher for managed clusters.
Instead use the [IBM Cloud cluster list fetcher][ibm-cloud-cluster-list-fetcher].
* Behavior: Retrieve stand-alone Kubernetes cluster resource data for the provided
list of clusters.  TTL is set to 1 day.
* Configuration elements:
  * `org.kubernetes.cluster_resources.clusters`
    * Required
    * List of dictionaries:
      * `account name`: An arbitrary IBM Cloud account name as a string
      * `server` A URL as a string to a Kubernetes stand-alone cluster
  * `org.kubernetes.cluster_resources.types`
    * Optional
    * List of resource types as strings
      * NOTE: For core group API resources, the resource name must be in
      _plural form_.  See example below.
      * NOTE: For other "custom" API resources, the resource name must be in the
      following format: `"APIGROUP/VERSION/NAME"`.  See example below.
    * Use if looking to override the default of `["nodes", "pods", "configmaps"]`.
    Otherwise do not include.
* Expected configuration:

  ```json
  {
    "org": {
      "kubernetes": {
        "cluster_resources": {
          "clusters": [
            {
              "account": "myaccount1",
              "server": "https://myserver1:30000"
            }
          ],
          "types": ["nodes", "pods", "apigroup.example.com/v1/mycustom"]
        }
      }
    }
  }
   ```


* Required credentials:
  * Kubernetes API server token with read/view permissions are needed for this fetcher to successfully retrieve the evidence.
    * `XXX_token`: token string for account `XXX`.
    * Example credential file entry:

      ```ini
      [kubernetes]
      myaccount1_token=your-kubernetes-api-token-1
      myaccount2_token=your-kubernetes-api-token-2
      ```

    * Expected Travis environment variable settings to generate credentials:
      * `KUBERNETES_MYACCOUNT1_TOKEN`
      * `KUBERNETES_MYACCOUNT2_TOKEN`

* Import statement:

   ```python
   from arboretum.kubernetes.fetchers.fetch_cluster_resource import ClusterResourceFetcher
   ```

## Checks

Checks coming soon...

[auditree-framework]: https://github.com/ComplianceAsCode/auditree-framework
[auditree-framework documentation]: https://complianceascode.github.io/auditree-framework/
[usage]: https://github.com/ComplianceAsCode/auditree-arboretum#usage
[fetch-cluster-resource]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/kubernetes/fetchers/fetch_cluster_resource.py
[ibm-cloud-cluster-list-fetcher]: https://github.com/ComplianceAsCode/auditree-arboretum/tree/main/arboretum/ibm_cloud#cluster-list

