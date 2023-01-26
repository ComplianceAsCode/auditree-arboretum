# Contributing

If you want to add to arboretum, please familiarize yourself with the code & our [Coding Standards][]. Make a fork of the repository & file a Pull Request from your fork with the changes. You will need to click the checkbox in the template to show you agree to the [Developer Certificate of Origin](https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/DCO1.1.txt).

If you make **regular & substantial contributions** to Auditree, you may want to become a collaborator. This means you can approve pull requests (though not your own) & create releases of the tool. Please [file an issue][new collab] to request collaborator access. A collaborator supports the project, ensuring coding standards are met & best practices are followed in contributed code, cutting & documenting releases, promoting the project etc.

If you would like to contribute fetchers, checks, or harvest reports please reference the [main README][Arboretum] in this repo.

## Code formatting and style

Please ensure all code contributions are formatted by `black` and pass all `flake8` linter requirements.
CI/CD will run `yapf` and `flake8` on all new commits and reject changes if there are failures.  If you
run `make develop` to setup and maintain your virtual environment then `black` and `flake8` will be executed
automatically as part of all git commits.  If you'd like to run things manually you can do so locally by using:

```shell
make code-format
make code-lint
```

## Testing

Please ensure all code contributions when appropriate are covered by appropriate unit tests and that all tests run cleanly.
CI/CD will run tests on all new commits and reject changes if there are failures.  Unit tests are required for all harvest
reports contributed to the library, all evidence helper classes, and all utility classes and functions outside of the
scope of fetchers and checks.  Fetchers and checks themselves do not at this time require unit tests due to the fact that
they are unit tests themselves. More to come on the testing of fetchers and checks in the future...

You should run the test suite locally by using:

```shell
make test
```

## Releases and change logs

We follow [semantic versioning][semver] and [changelog standards][changelog] with
the following addendum:

- We set the main package `__init__.py` `version` for version tracking.
- Our change log is CHANGES.md.
- In addition to the _types of changes_ outlined in the
[changelog standards][changelog] we also include a BREAKING _type of change_ to
call out any change that may cause downstream execution disruption.
- Change types are always capitalized and enclosed in square brackets.  For
example `[ADDED]`, `[CHANGED]`, etc.
- Changes are in the form of complete sentences with appropriate punctuation.

[semver]: https://semver.org/
[changelog]: https://keepachangelog.com/en/1.0.0/#how
[Arboretum]: https://github.com/ComplianceAsCode/auditree-arboretum
[Coding Standards]: https://complianceascode.github.io/auditree-framework/coding-standards.html
[new collab]: https://github.com/ComplianceAsCode/auditree-arboretum/issues/new?template=new-collaborator.md
