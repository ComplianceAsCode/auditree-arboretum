# Kubernetes library

The fetchers and checks contained within this `kubernetes` category folder are
common tests that can be configured and executed for the purpose of generating
compliance reports and notifications using the [auditree-framework][].  They
validate the configuration and ensure smooth execution of an auditree instance.
See [auditree-framework documentation](https://complianceascode.github.io/auditree-framework/)
for more details.

These tests are normally executed by a CI/CD system like
[Travis CI](https://travis-ci.com/) as part of another project that uses this
library package as a dependency.

## Usage as a library

See [usage][usage] for specifics on including this library as a dependency and
how to include the fetchers and checks from this library in your downstream project.

## Fetchers

### Cluster List

* Class: [ClusterListFetcher][fetch-cluster-list]
* Purpose: Write the list of kubernetes clusters to the evidence locker.
* Behavior: Read BOM (Bill of Materials) data in config file and write it into `raw/kubernetes/cluster_list.json`. 
* Expected configuration elements:
  * org.kubernetes.cluster_list.config.bom
    * List of target kubernetes clusters (see example below)
* Expected configuration example:
   ```json
   {
     "org": {
       "kubernetes": {
         "cluster_list": {
           "config": {
             "bom": [
               {
                 "account": "ibmcloud_myaccount",
                 "name": "mycluster-free",
                 "kubeconfig": "/home/myaccount/.kube/mycluster-free.kubeconfig",
                 "type": "kubernetes"
               }
             ]
           }
         }
       }
     }
   }
   ```
* Expected credentials:
  * A kubeconfig file specified in org.kube.cluster_list.config.bom[].kubeconfig of config file must be a valid kubeconfig file.
* Import statement:
   ```python
   from arboretum.kubernetes.fetchers.fetch_cluster_list import ClusterListFetcher
   ```

### Cluster Resource

* Class: [ClusterResourceFetcher][fetch-cluster-resource]
* Purpose: Write the resources of clusters to the evidence locker.
* Behavior: Read a cluster list from `raw/CATEGORY/cluster_list.json` where `CATEGORY` is the category name specified in configuration, and fetch resources from the clusters.  Fetch target resource types can be specified in config file.
* Expected configuration elements:
  * org.kubernetes.cluster_resource.config
    * `cluster_list_types`: cluster list types (same as category names) - for example, specify `kubernetes` if you want to read the cluster list by [ClusterListFetcher of kubernetes][fetch-cluster-list], and specify `ibm_cloud` if you want to read the cluster list by [ClusterListFetcher of ibm_cloud][fetch-cluster-list-ibmcloud].
    * `target_resource_types`: list of target resource types (default: [`node`, `configmap`])
* Expected configuration example:
   ```json
   {
     "org": {
       "kubernetes": {
         "cluster_resource": {
           "config": {
             "cluster_list_types": [
               "kubernetes", "ibm_cloud"
             ],
             "target_resource_types": [
               "node"
             ]
           }
         }
       }
     }
   }
   ```
* Expected credentials:
  * Credentials (including kubeconfig file) are required for the clusters specified in the configuration.  See documents of cluster list fetchers ([ClusterListFetcher of kubernetes][fetch-cluster-list], [ClusterListFetcher of ibm_cloud][fetch-cluster-list-ibmcloud]) because the cluster resource fetcher also use the credentials for the list fetchers.
* Import statement:

   ```python
   from arboretum.kubernetes.fetchers.fetch_cluster_resource import ClusterResourceFetcher
   ```


## Checks

Checks coming soon...

[usage]: https://github.com/ComplianceAsCode/auditree-arboretum#usage
[fetch-cluster-list]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/kubernetes/fetchers/fetch_cluster_list.py
[fetch-cluster-list-ibmcloud]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/ibm_cloud/fetchers/fetch_cluster_list.py
[fetch-cluster-resource]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/kubernetes/fetchers/fetch_cluster_resource.py
