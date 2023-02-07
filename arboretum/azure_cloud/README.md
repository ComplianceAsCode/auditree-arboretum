# Azure Cloud library

The fetchers and checks contained within this `azure_cloud` category folder are
common tests that can be configured and executed for the purpose of generating
compliance reports and notifications using the [auditree-framework][auditree-framework].
See [auditree-framework documentation][auditree-framework documentation] for more details.

These tests are normally executed by a CI/CD system like
[Travis CI](https://travis-ci.com/) as part of another project that uses this
library package as a dependency.

## Usage as a library

See [usage][usage] for specifics on including this library as a dependency and how
to include the fetchers and checks from this library in your downstream project.

## Fetchers

### Assessments List

* Class: [AssessmentsListFetcher][fetch-assessments]
* Purpose: Write the list of Azure Cloud assessments to the evidence locker.
* Behavior: Access [Azure Cloud API][azure-cloud-api-assessments] and save the list of assessments bound with specified account.
* Configuration elements:
  * `org.azure_cloud.accounts`
    * Required
    * List of accounts (string)
    * Each account is an arbitrary name describing the Azure Cloud account. It is used to match to the token provided in the
      credentials file in order for the fetcher to retrieve content from Azure Cloud for that account.
* Example (required) configuration:

  ```json
  {
    "org": {
      "azure_cloud": {
        "accounts": ["myaccount1"]
      }
    }
  }
  ```

* Required credentials:
  * `azure_cloud` credentials with read permissions are needed for this fetcher to successfully retrieve the evidence.
    * `myaccount1_clientid`: The Application(client) ID of Azure [Service Principal][SPN] in Azure Active Directory.
    * `myaccount1_clientsecret`: The Application(client) secret of Azure [Service Principal][SPN] in Azure Active Directory.
    * `myaccount1_subscriptionid`: Your azure subscriptioin id.
    * `myaccount1_tenantid`: Your azure tenant id.
    * Example credential file entry:

      ```ini
      [azure_cloud]
      myaccount1_clientid=your-azure-cloud-app-client-id
      myaccount1_clientsecret=your-azure-cloud-app-client-secret
      myaccount1_subscriptionid=your-azure-subscription-id
      myaccount1_tenantid=your-azure-tenant-id
      ```

    * NOTE: An Azure [Service Principal][SPN] is a security identity used by user-created applications, services, and automation tools to access specific Azure resources. Assign your application client of SPN to the role of "Reader" under the given your subscription and grant MS Graph API permissions.

* Import statement:

   ```python
   from arboretum.azure_cloud.fetchers.fetch_assessments import AssessmentsListFetcher
   ```

### Assessments MetaData List

* Class: [AssessmentsMetaDataListFetcher][fetch-assessments-metadata]
* Purpose: Write the list of Azure Cloud assessments metadata to the evidence locker.
* Behavior: Access [Azure Cloud API][azure-cloud-api-assessments-metadata] and save the list of assessments metadata bound with specified account.
* Configuration elements:
  * `org.azure_cloud.accounts`
    * Required
    * List of accounts (string)
    * Each account is an arbitrary name describing the Azure Cloud account. It is used to match to the token provided in the
      credentials file in order for the fetcher to retrieve content from Azure Cloud for that account.
* Example (required) configuration:

  ```json
  {
    "org": {
      "azure_cloud": {
        "accounts": ["myaccount1"]
      }
    }
  }
  ```

* Required credentials: Same with assessments list fetcher

* Import statement:

   ```python
   from arboretum.azure_cloud.fetchers.fetch_assessments_metadata import AssessmentsMetaDataListFetcher
   ```

### Sub Assessments List

* Class: [SubAssessmentsListFetcher][fetch-sub-assessments]
* Purpose: Write the list of Azure Cloud sub assessments to the evidence locker.
* Behavior: Access [Azure Cloud API][azure-cloud-api-sub-assessments] and save the list of sub assessments bound with specified account.
* Configuration elements:
  * `org.azure_cloud.accounts`
    * Required
    * List of accounts (string)
    * Each account is an arbitrary name describing the Azure Cloud account. It is used to match to the token provided in the
      credentials file in order for the fetcher to retrieve content from Azure Cloud for that account.
* Example (required) configuration:

  ```json
  {
    "org": {
      "azure_cloud": {
        "accounts": ["myaccount1"]
      }
    }
  }
  ```

* Required credentials: Same with assessments list fetcher

* Import statement:

   ```python
   from arboretum.azure_cloud.fetchers.fetch_sub_assessments import SubAssessmentsListFetcher
   ```

## Checks

Checks coming soon...

[auditree-framework]: https://github.com/ComplianceAsCode/auditree-framework
[auditree-framework documentation]: https://complianceascode.github.io/auditree-framework/
[usage]: https://github.com/ComplianceAsCode/auditree-arboretum#usage
[azure-cloud-api-assessments]: https://docs.microsoft.com/en-us/rest/api/securitycenter/assessments
[azure-cloud-api-sub-assessments]: https://docs.microsoft.com/en-us/rest/api/securitycenter/sub-assessments
[azure-cloud-api-assessments-metadata]: https://docs.microsoft.com/en-us/rest/api/securitycenter/assessments-metadata
[fetch-assessments]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/azure_cloud/fetchers/fetch_assessments.py
[fetch-sub-assessments]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/azure_cloud/fetchers/fetch_sub_assessments.py
[fetch-assessments-metadata]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/azure_cloud/fetchers/fetch_assessments_metadata.py
[SPN]: https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal
