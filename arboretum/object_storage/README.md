# Object Storage library

The fetchers and checks contained within this `object_storage` category folder are
common tests that can be configured and executed for the purpose of generating
compliance reports and notifications using the [auditree-framework][].  They
validate the configuration and ensure smooth execution of an auditree instance.
See [auditree-framework documentation][] for more details.

These tests are normally executed by a CI/CD system like
[Travis CI](https://travis-ci.com/) as part of another project that uses this
library package as a dependency.

## Usage as a library

See [usage][] for specifics on including this library as a dependency and
how to include the fetchers and checks from this library in your downstream project.

## Fetchers

### COS Metadata

* Class: [COSMetadataFetcher][fetch-cos-metadata]
* Purpose: Store COS bucket metadata including encryption status.
* Behavior: Access COS instances and all of their buckets to get metadata of each bucket including server-side encryption status.

* Expected configuration elements:
  * org.cos.accounts: an object keyed on account names of COS instances.
  * Each object must contain key value pairs of IBM Cloud region (e.g., `us-south`, `jp-tok`) and the list of COS service instance names to be retrieved in that region.
* Expected configuration:

```json
  "org": {
    "cos": {
      "accounts": {
        "my_account": {
            "us-south": ["instance_1", "instance_2"]
        }
      }
    }
  }
```

* Expected credentials:
  * `github_enterprise` credentials with repository admin permissions are needed for this fetcher to successfully
   retrieve the evidence.
    * `username`: The Github Enterprise user used to run the fetcher.
    * `token`: The Github Enterprise user access token used to run the fetcher.

      ```ini
      [github_enterprise]
      username=ghe-user-name
      token=ghe-access-token
      ```

    * Expected Travis environment variable names to generate credentials:
      * `GITHUB_ENTERPRISE_USERNAME`
      * `GITHUB_ENTERPRISE_TOKEN`

  * NOTE: These credentials are also needed for basic configuration of the compliance automation framework and for
   repository integrity usage.  The expectation is that the same set of Github credentials are used for all Github access.
  * `ibm_cloud` credentials with read/view permissions are needed for this fetcher to successfully retrieve the evidence.
    * One API key is required per account specified in the configuration, e.g `cos_tm1` above. Each account provided in the configuration must preceed _api_key. For example, if we have specified accounts "acct_a", "acct_b", and "acct_c" your configuration should look like:

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
from arboretum.object_storage.fetchers.fetch_cos_metadata import COSMetadataFetcher
```


## Checks

* Class: [COSBucketEncryptionKeyCheck][cosbucketencryptionkeycheck]
* Purpose: Verifies the keys used to encrypt COS buckets in accounts.
* Behavior: Confirms that a customer managed key is used to encrypt buckets.
* Evidence depended upon:
  * COS Metadata
    * `raw/cos/cos_bucket_metadata.json`
    * Gathered by the `cos` provider [COSMetadataFetcher][fetch-cos-metadata]
* Expected configuration elements:
  * `org.cos.encryption.exclude`
    * Optional
    * List of strings
    * Provide bucket URLs to warn not error on
    * Use if there are buckets that do not need to be encrypted with customer key
* Expected configuration (optional):

```json
{
 "org": {
    "name": "xylon",
    "cos": {
      "encryption": {
        "exclude": [
          "https://s3.us-south.cloud-object-storage.appdomain.cloud/my-nonsensative-bucket"
        ]
      }
    }
  }
}
```

* Import statement:

```python
from arboretum.object_storage.checks.test_cos_bucket_encryption import COSBucketEncryptionKeyCheck
```

### COS Bucket Expired Encryption Key

* Class: [COSBucketEncryptionKeyValidCheck][cosbucketencryptionkeyvalidcheck]
* Purpose: Verifies the keys used to encrypt COS buckets are considered valid.
* Behavior: Verifies (based on configuration) that the keys in use are valid.
* Evidence depended upon:
  * COS Metadata
    * `raw/cos/cos_bucket_metadata.json`
    * Gathered by the `cos` provider [COSMetadataFetcher][fetch-cos-metadata]
* Expected configuration elements:
  * `org.cos.encryption.expired_keys`
    * Optional
    * List of strings
    * Provide CRNs of KeyProtect keys you want to mark as expired
    * Use to identify buckets using an encryption key you no longer consider valid
* Expected configuration (optional):

```json
{
 "org": {
    "name": "xylon",
    "cos": {
      "encryption": {
        "expired_keys": [
          "crn:v1:bluemix:public:kms:us-south:my_duff_key"
        ]
      }
    }
  }
}
```

* Import statement:

```python
from arboretum.object_storage.checks.test_cos_expired_keys import COSBucketEncryptionKeyValidCheck
```


[auditree-framework]: https://github.com/ComplianceAsCode/auditree-framework
[auditree-framework documentation]: https://complianceascode.github.io/auditree-framework/
[usage]: https://github.com/ComplianceAsCode/auditree-arboretum#usage
