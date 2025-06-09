## v4.0.1 (2025-06-09)

### Build System(s)

- remove pylint, add ruff lint ignore rules
- update ckantools

### CI System(s)

- set ruff target py version, add more ignores - avoid using fixes that don't work for python 3.8 (our current version) - ignore recommended ruff formatter conflicts - ignore more docstring rules
- add ruff lint select rules
- update pre-commit repo versions

## v4.0.0 (2025-04-19)

### Breaking Changes

- upgrade for compatibility with new vds version

### Feature

- upgrade for compatibility with new vds version

### Fix

- use correct parameter for IIIF modifications

### Tests

- fix the tests

## v3.0.12 (2024-11-04)

### Docs

- use variable logo based on colour scheme
- fix tests badge tests workflow file was renamed
- standardise returns field

### Style

- automatic reformat auto reformat with ruff/docformatter/prettier after config changes

### Build System(s)

- remove version from docker compose file version specifier is deprecated

### CI System(s)

- fix python setup action version
- add merge to valid commit types
- add docformatter args and dependency docformatter currently can't read from pyproject.toml without tomli
- only apply auto-fixes in pre-commit F401 returns linting errors as well as auto-fixes, so this disables the errors and just applies the fixes
- update tool config update pre-commit repo versions and switch black to ruff
- add pull request validation workflow new workflow to check commit format and code style against pre-commit config
- update workflow files standardise format, change name of tests file

### Chores/Misc

- add pull request template
- update tool details in contributing guide

## v3.0.11 (2024-08-20)

## v3.0.10 (2024-03-11)

### Fix

- redirect canvas links to main iiif manifest
- use _id field as title if title field not in record

### Chores/Misc

- add build section to read the docs config
- add regex for version line in citation file
- add citation.cff to list of files with version
- add contributing guidelines
- add code of conduct
- add citation file
- update support.md links

## v3.0.9 (2023-07-17)

### Docs

- update logos

## v3.0.8 (2023-05-09)

### Fix

- allow the images in a manifest to be correctly opened in mirador etc

### Tests

- fix the basic manifest test

## v3.0.7 (2023-04-11)

### Build System(s)

- fix postgres not loading when running tests in docker

### Chores/Misc

- add action to sync branches when commits are pushed to main

## v3.0.6 (2023-02-20)

### Docs

- fix api docs generation script

### Chores/Misc

- small fixes to align with other extensions

## v3.0.5 (2023-01-31)

### Docs

- **readme**: change logo url from blob to raw

## v3.0.4 (2023-01-31)

### Docs

- **readme**: direct link to logo in readme
- **readme**: fix github actions badge

## v3.0.3 (2023-01-30)

### Build System(s)

- **docker**: use 'latest' tag for test docker image

## v3.0.2 (2022-12-12)

### Build System(s)

- include top-level data files in theme folder
- add package data

## v3.0.1 (2022-12-01)

### Fix

- use not instead of is None to catch empty strings too
- fix the build_iiif_identifier action

### Docs

- **readme**: format test section
- **readme**: update installation steps
- **readme**: update ckan patch version in header badge

### Style

- use single quotes

### Tests

- Add breaking test to confirm build_iiif_identifier action failure

## v3.0.0 (2022-11-28)

### Breaking Changes

- The IIIIF interface has been changed.

### Feature

- add a new action "build_iiif_identifier" to allow callers to create identifiers for known builders
- switch the builders list to an OrderedDict so that a name can be stored against each builder function
- move IIIF resource generation to actions and refactor most of the code

### Fix

- stop producing manifests if no images are available on a record
- change case on plugin name
- exclude helpers from tests
- unpin ckantools version

### Refactor

- refactor the builder functions to an abc to accommodate future planned changes

### Docs

- **README.md**: update the docs to include the new class based style
- **README.md**: update the documentation for extending the IIIF resource builders
- **README.md**: add documentation about what is included in the extension and how to extend it
- **README.md**: update the readme overview section
- fix markdown-include references
- add section delimiters
- add logo

### Style

- **README.md**: reformat the README
- apply formatting changes

### Tests

- add more tests for the updated _build_record_manifest_id function

### Build System(s)

- set changelog generation to incremental
- pin ckantools minor version

### CI System(s)

- add cz_nhm as a dependency
- **commitizen**: fix message template
- add pypi release action

### Chores/Misc

- use cz_nhm commitizen config
- improve commitizen message template
- move cz config into separate file
- standardise package files

## v2.1.0 (2022-05-30)

## v2.0.0 (2021-03-09)
