# IBM Cloud Databases library

The fetchers and checks contained within this `ibm_cloud_databases` category folder are
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

### IBM Cloud Databases List

* Class: [DatabasesFetcher][fetch-databases]
* Purpose: Store list of account-specific IBM Cloud databases to the evidence locker.
* Behavior: Retrieve details about account specific IBM Cloud Databases. TTL for evidence is set to 1 day.
* Configuration elements:
  * `org.icd.list.accounts`
    * Required
    * List of dictionaries representing the IBM Cloud accounts
    * Each dictionary must have the following fields
      * `account_name` - an arbitrary name as a string identifying the IBM Cloud account, used to match to the token provided in the
      credentials file in order for the fetcher to retrieve content from IBM Cloud for that account.
      * `resource_group_id` - the resource group id's as a list of strings, associated with the above account name, output of [running the ibmcloud resource groups command][ic-resource-groups] while logged in to an IBM Cloud account.

* Example (required) configuration:

  ```json
  {
    "org": {
      "icd": {
        "list": {
          "accounts": [
            {
              "account_name": "prod_1234567",
              "resource_group_id": [
                                        "bcdef0123456789fedcba1234567890a",
                                        "a0987654321abcdef9876543210fedcb",
                                   ]
            }
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
   from arboretum.ibm_cloud_databases.fetchers.fetch_cluster_list import DatabasesFetcher
   ```

### IBM Cloud Databases Backups

* Class: [DatabaseBackupsFetcher][fetch-backups]
* Purpose: Store details of recent backups of account-specific IBM Cloud databases to the evidence locker.
* Behavior: Retrieves the details of the recent backups as a JSON array. TTL for evidence is set to 1 day.
* NOTE: This fetcher depends on evidence collected by the [IBM Cloud Databases List fetcher](#ibm-cloud-databases-list), i.e. importing the IBM Cloud Databases List fetcher is a prerequisite for the IBM Cloud Databases Backups fetcher to work.

* Expected configuration elements: See [IBM Cloud Databases List fetcher](#ibm-cloud-databases-list) expected configuration elements.

## Checks

Checks coming soon...

[auditree-framework]: https://github.com/ComplianceAsCode/auditree-framework
[auditree-framework documentation]: https://complianceascode.github.io/auditree-framework/
[usage]: https://github.com/ComplianceAsCode/auditree-arboretum#usage
[ic-api-key-create]: https://cloud.ibm.com/docs/cli/reference/ibmcloud?topic=cloud-cli-ibmcloud_commands_iam#ibmcloud_iam_api_key_create
[fetch-databases]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/ibm_cloud_databases/fetchers/fetch_databases.py
[fetch-backups]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/ibm_cloud_databases/fetchers/fetch_backups.py
[ibm-cloud-api]: https://containers.cloud.ibm.com/
[ibm-cloud-gen-api-console]: https://cloud.ibm.com/docs/account?topic=account-userapikey#create_user_key
[ic-resource-groups]: https://cloud.ibm.com/docs/cli/reference/ibmcloud?topic=cloud-cli-ibmcloud_cli#global-option-output-examples