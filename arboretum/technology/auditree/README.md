# Auditree technology library

The fetchers and checks contained within this `auditree` technology folder are common tests that can be configured and
executed for the purpose of generating compliance reports and notifications using the [auditree-framework][].
See [auditree-framework documentation](https://complianceascode.github.io/auditree-framework/) for more details.

These tests are normally executed by a CI/CD system like [Travis CI](https://travis-ci.com/) as part of another project
that uses this library package as a dependency.

## Usage as a library

See [usage][usage] for specifics on including this library as a dependency and how to include the fetchers and checks
from this library in your downstream project.

## Fetchers

### Abandoned Evidence

* Class: [AbandonedEvidenceFetcher][fetch-abandoned-evidence]
* Purpose: Writes evidence that has been identified as abandoned to the evidence locker.
* Behavior: Stores abandoned evidence and abandoned evidence exceptions to the evidence locker.  If the optional
`threshold` configuration setting is applied then abandoned evidence is identified as evidence that has not been
updated in over that `threshold` value otherwise the default is 30 days.  TTL is set to 1 day.
* Expected configuration elements:
   * org.auditree.abandoned\_evidence.threshold
      * Optional
      * Integer
      * Provide value in seconds
      * Use if looking to override the default of 30 days otherwise do not include.
   * org.auditree.abandoned\_evidence.exceptions
      * Optional
      * Dictionary where the key/value pairs are the path to the evidence (key) and the reason for excluding it from the
      abandoned evidence list (value).
      * Key/Value: String/String
      * Use if looking to exclude evidence files from being deemed abandoned and included as failures.  All "exceptions"
      will still appear on the report and will be treated as warnings rather than failures.
* Expected configuration (optional):

   ```json
   {
     "org": {
       "auditree": {
         "abandoned_evidence": {
           "threshold": 1234567,
           "exceptions": {
             "raw/path/to-evidence.json": "This is a good reason",
             "raw/path/to-evidence-2.json": "This is also a good reason"
           }
         }
       }
     }
   }
   ```
* Expected credentials:
   * None
* Import statement:

   ```python
   from arboretum.technology.auditree.fetchers.fetch_abandoned_evidence import AbandonedEvidenceFetcher
   ```

## Checks

### Abandoned Evidence

* Class: [AbandonedEvidenceCheck][check-abandoned-evidence]
* Purpose: For every piece of evidence that has not been updated for longer than the time to live plus the specified
threshold a failure is generated and reported.
* Behavior: Performs a check that compares abandoned evidence identified on a given check execution with the last time new
abandoned evidence was found and reports on newly found abandoned evidence and possible exceptions.  If no "abandoned
evidence" evidence is contained within the locker then this check traverses the evidence locker repository and
identifies evidence that has not been updated for a specific period of time and reports on abandoned evidence found for
the current check execution.  The default threshold is 30 days beyond the time to live (TTL) setting.
* Evidence depended upon:
   * Abandoned evidence and exceptions
      * `raw/auditree/abandoned_evidence.json`
      * Gathered by the `auditree` provider [AbandonedEvidenceFetcher][fetch-abandoned-evidence]
   * If the [AbandonedEvidenceFetcher][fetch-abandoned-evidence] is not used to store "abandoned evidence" evidence in
   the locker then the tooling performs a sweep of the evidence locker metadata to assess evidence that has not been
   updated in the timeframe specified.
* Expected configuration elements:
   * org.auditree.abandoned\_evidence.threshold
      * Optional
      * Integer
      * Provide value in seconds
      * Use if looking to override the default of 30 days otherwise do not include.
   * org.auditree.abandoned\_evidence.exceptions
      * Optional
      * Dictionary where the key/value pairs are the path to the evidence (key) and the reason for excluding it from the
      abandoned evidence list (value).
      * Key/Value: String/String
      * Use if looking to exclude evidence files from being deemed abandoned and included as failures.  All "exceptions"
      will still appear on the report and will be treated as warnings rather than failures.
   * org.auditree.abandoned\_evidence.ignore\_history
      * Optional
      * Boolean
      * Set to `true`
      * Use if collecting `raw/auditree/abandoned_evidence.json` in the evidence locker but intend to run the check
      without referencing the evidence history (more rigid alerts).  Otherwise do not include.
* Expected configuration (optional):

   ```json
   {
     "org": {
       "auditree": {
         "abandoned_evidence": {
           "threshold": 1234567,
           "exceptions": {
             "raw/path/to-evidence.json": "This is a good reason",
             "raw/path/to-evidence-2.json": "This is also a good reason"
           },
           "ignore_history": true
         }
       }
     }
   }
   ```

* Import statement:

   ```
   from arboretum.technology.auditree.checks.test_abandoned_evidence import AbandonedEvidenceCheck
   ```


[usage]: https://github.com/ComplianceAsCode/auditree-arboretum#usage
[fetch-abandoned-evidence]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/technology/auditree/fetchers/fetch_abandoned_evidence.py
[check-abandoned-evidence]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/technology/auditree/checks/test_abandoned_evidence.py
