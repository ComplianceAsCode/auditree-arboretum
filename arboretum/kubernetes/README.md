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

Fetchers coming soon...

## Checks

Checks coming soon...

## Reports

### Compliance OSCAL Observations 

* Report: [compliance_oscal_observations][compliance-oscal-observations]
* Purpose: Create a JSON format report as a [NIST OSCAL Assessment Results][assessment-results] observations list from the kubernetes [OpenShift Compliance Operator][compliance-operator] data in the evidence locker.
* Behavior: 
    * A report is generated comprising a collection of observations, one for each [XCCDF][xccdf] rule/result pair discovered in the `cluster_resource.json` files with respect to the optional date range. Each observation may be enhanced in accordance with an optional `oscal_metadata.yaml` file.
* Data files required:
    * `raw/kubernetes/cluster_resource.json`, created by the kubernetes provider [ClusterResourceFetcher][fetch-cluster-resource].
* Data files optional:
    * `raw/kubernetes/oscal_metadata.json`, planted by the kubernetes provider account administrator.
* Details/Config:

   ```shell
   harvest reports arboretum --detail compliance_oscal_observations
   ```

[compliance-oscal-observations]: https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/kubernetes/reports/compliance_oscal_observations.py
[fetch-cluster-resource]: https://github.ibm.com/auditree/auditree-central/blob/master/auditree_central/provider/iks/fetchers/fetch_cluster_resource.py
[assessment-results]: https://pages.nist.gov/OSCAL/documentation/schema/assessment-results-layer/assessment-results/
[xccdf]: https://csrc.nist.gov/projects/security-content-automation-protocol/specifications/xccdf
[compliance-operator]: https://github.com/openshift/compliance-operator/blob/master/README.md
[auditree-framework]: https://github.com/ComplianceAsCode/auditree-framework
[auditree-framework documentation]: https://complianceascode.github.io/auditree-framework/
[usage]: https://github.com/ComplianceAsCode/auditree-arboretum#usage
