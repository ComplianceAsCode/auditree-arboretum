# IBM Cloud library

The fetchers and checks contained within this `ibm_cloud` category folder are
common tests that can be configured and executed for the purpose of generating
compliance reports and notifications using the [auditree-framework](https://github.com/ComplianceAsCode/auditree-framework).  They
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
* Purpose: Write the list of IBM Cloud clusters to the evidence locker.
* Behavior: Log in to IBM Cloud using `ibmcloud login` command, and save the result of `ibmcloud cs cluster ls` command.
* Expected configuration elements:
  * org.ibm_cloud.cluster_list.config
    * List of objects representing the IKS accounts
    * Each object must have the following values
      * `account` - a list containing names identifying the IKS account, this will map to an IAM token provided in the credentials file
* Expected configuration example:
   ```json
   {
     "org": {
       "ibm_cloud": {
         "cluster_list": {
           "config": {
               "account": ["myaccount1"]
           }
         }
       }
     }
   }
   ```
* <a name="expected_credentials"></a>Expected credentials:
  * `ibm_cloud` credentials with read/view permissions are needed for this fetcher to successfully
   retrieve the evidence.
    * One IKS API key is required per account specified in the configuration.  See above.  Each account provided in the configuration must preceed `_api_key`.  For example, if we have specified accounts "acct_a", "acct_b", and "acct_c" your configuration should look like:

      ```ini
      [ibm_cloud]
      acct_a_api_key=your-iks-api-key-for-acct-a
      acct_b_api_key=your-iks-api-key-for-acct-b
      acct_c_api_key=your-iks-api-key-for-acct-c
      ```

    * Expected Travis environment variable settings to generate credentials:
      * `IBM_CLOUD_ACCT_A_API_KEY`
      * `IBM_CLOUD_ACCT_B_API_KEY`
      * `IBM_CLOUD_ACCT_C_API_KEY`

  * NOTE: [API Keys can be generated using the ibmcloud CLI][ic-api-key-create]. E.g.

      ```sh
      ibmcloud iam api-key-create your-iks-api-key-for-acct-x
      ```
* Import statement:

   ```python
   from arboretum.ibm_cloud.fetchers.fetch_cluster_list import ClusterListFetcher
   ```

## Checks

Checks coming soon...

[usage]: https://github.com/ComplianceAsCode/auditree-arboretum#usage
[ic-api-key-create]: https://cloud.ibm.com/docs/cli/reference/ibmcloud?topic=cloud-cli-ibmcloud_commands_iam#ibmcloud_iam_api_key_create
[fetch-cluster-list]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/ibm_cloud/fetchers/fetch_cluster_list.py