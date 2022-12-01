# Changelog

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

- change case on plugin name
- exclude helpers from tests
- stop producing manifests if no images are available on a record
- unpin ckantools version

### Refactor

- refactor the builder functions to an abc to accommodate future planned changes

### Docs

- fix markdown-include references
- add section delimiters
- **README.md**: update the docs to include the new class based style
- **README.md**: update the documentation for extending the IIIF resource builders
- **README.md**: add documentation about what is included in the extension and how to extend it
- **README.md**: update the readme overview section
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
