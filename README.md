<img src=".github/nhm-logo.svg" align="left" width="150px" height="100px" hspace="40"/>

# ckanext-iiif

[![Tests](https://img.shields.io/github/workflow/status/NaturalHistoryMuseum/ckanext-iiif/Tests?style=flat-square)](https://github.com/NaturalHistoryMuseum/ckanext-iiif/actions/workflows/main.yml)
[![Coveralls](https://img.shields.io/coveralls/github/NaturalHistoryMuseum/ckanext-iiif/main?style=flat-square)](https://coveralls.io/github/NaturalHistoryMuseum/ckanext-iiif)
[![CKAN](https://img.shields.io/badge/ckan-2.9.1-orange.svg?style=flat-square)](https://github.com/ckan/ckan)
[![Python](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue.svg?style=flat-square)](https://www.python.org/)
[![Docs](https://img.shields.io/readthedocs/ckanext-iiif?style=flat-square)](https://ckanext-iiif.readthedocs.io)

_IIIF for CKAN_

# Overview

This extension enables IIIF functionality for CKAN by implementing the Presentation API.
Currently, this includes a single manifest builder for records, but through the `IIIIF`
interface you can extend the builders to include other IIIF resources.

# Installation

Path variables used below:

- `$INSTALL_FOLDER` (i.e. where CKAN is installed), e.g. `/usr/lib/ckan/default`
- `$CONFIG_FILE`, e.g. `/etc/ckan/default/development.ini`

1. Clone the repository into the `src` folder:

  ```bash
  cd $INSTALL_FOLDER/src
  git clone https://github.com/NaturalHistoryMuseum/ckanext-iiif.git
  ```

2. Activate the virtual env:

  ```bash
  . $INSTALL_FOLDER/bin/activate
  ```

3. Install the requirements from requirements.txt:

  ```bash
  cd $INSTALL_FOLDER/src/ckanext-iiif
  pip install -r requirements.txt
  ```

4. Run setup.py:

  ```bash
  cd $INSTALL_FOLDER/src/ckanext-iiif
  python setup.py develop
  ```

5. Add 'iiif' to the list of plugins in your `$CONFIG_FILE`:

  ```ini
  ckan.plugins = ... iiif
  ```

# Configuration

There are no configuration options for this extension.

# Usage

This extension's main function is provide a standard endpoint and action to create IIIF
resources.
These IIIF resources could be based on whatever you like - a record, a resource, a whole
dataset etc.

Presentation API IIIF resources can be accessed via either the `/iiif/<identifier>`
endpoint or the `build_iiif_resource` action where the identifier is passed in the data
dict in the key `"identifier"`.
When this occurs the identifier is matched against any of the registered IIIF resource
builders and if a match is found, the resource is returned.

## Record Manifest Builder

By default, the only IIIF resource this extension can build is record manifests.
This requires the `record_show` action to be available from the `ckanext-nhm` extension
(there is
an [open issue](https://github.com/NaturalHistoryMuseum/ckanext-nhm/issues/602) to move
this action to a different extension, most likely
[ckanext-versioned-datastore](https://github.com/NaturalHistoryMuseum/ckanext-versioned-datastore))
.

To build a record manifest you must provide the appropriate identifier, which must be of
the format `resource/<resource_id>/record/<record_id>`, for example:
`resource/afea211d-1b3d-49ad-9d15-17f0de368967/record/429`.
This example identifies the record with ID `429` from the resource with ID
`afea211d-1b3d-49ad-9d15-17f0de368967`.
If the record and the resource can be found, and images can be found on the record, then
a manifest is returned.
If any of these conditions fail, the action returns `None` and the endpoint returns 404.

The images are detected in the record by looking for the `_image_field` extra on the
resource.
This should define the field name in the record where images can be found.
The value associated with this image field in the record can be:

- a string (should be a URL)
- a list of strings (each element should be a URL)
- a string containing several URLs separated by a delimiter (this should be defined on
  the resource using the `_image_delimiter` extra)
- a list of dicts (the URL is extracted by looking for an `identifier` field within
  each dict)

To fill out the values in the manifest, the builder pulls out fields as specified by
more resource level extras or by falling back to a default value.
These are:

- `"label"` - attempts to use `_title_field` extra but falls back to record ID
- `"rights"` - attempts to use `_image_licence` extra but falls back
  to [cc-by](https://creativecommons.org/licenses/by/4.0/)

The `"metadata"` field in the manifest is populated using the fields and values in the
record data itself.

## Adding a Custom Builder

To add a custom builder all you have to do is implement the `IIIIF` interface in your
extension plugin.
For example:

```python
import ckan.plugins as plugins
from ckanext.iiif.interfaces import IIIIF
from typing import Optional, Callable, List


def my_builder(identifier: str) -> Optional[dict]:
    ...


class MyExtension(plugins.SingletonPlugin):
    plugins.implements(IIIIF)

    def register_iiif_builders(self, builders: List[Callable[[str], Optional[dict]]]):
        builders.append(my_builder)
```

When a request is made to build a IIIF resource, each of the registered builders is
called in turn with the identifier.
This means that the builders need to both match the identifier to confirm it matches its
pattern or meets its criteria, and generate the manifest.

The builders should:

- Return `None` if the identifier doesn't match the builders requirements. When this
  happens, the logic continues and tries the next registered builder function.
- Raise a `ckanext.iiif.builders.utils.IIIFBuildError` if the identifier matched but the
  manifest couldn't be generated for any reason. This will stop the logic from checking
  any other builders for matches and return `None` to the caller.
- Raise any other type of `Exception` if an unexpected error occurred during matching or
  processing. This will be propagated to the caller.

# Testing

There is a Docker compose configuration available in this repository to make it easier
to run tests.

To run the tests against ckan 2.9.x on Python3:

1. Build the required images

```bash
docker-compose build
```

2. Then run the tests.
   The root of the repository is mounted into the ckan container as a volume by the
   Docker compose
   configuration, so you should only need to rebuild the ckan image if you change the
   extension's
   dependencies.

```bash
docker-compose run ckan
```

The ckan image uses the Dockerfile in the `docker/` folder.
