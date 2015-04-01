""" Module for managing configurations.

Each configuration should be a sub-package named with the specified prefix
(normally 'cfg_') and preferably with a name that semantically describes the
configuration purpose.

Each configuration package should contain a module named main.py and one
module per version of the configuration JSON schema, named 'schema_' and the
version number separated by underscores instead of dots.
Example:

    my_configs
    ├── cfg_user_properties.py
    │   ├── __init__.py
    │   ├── main.py
    │   └── schema_1_0_0.py
    ├── cfg_customer_properties
    │   ├── __init__.py
    │   ├── main.py
    │   ├── schema_1_1_0.py
    │   └── schema_1_0_0.py
    └── __init__.py

The configuration versioning roughly follows "Semantic Versioning 2.0.0".
(For more information about Semantic Versioning, go to http://semver.org/)
Example:

    MAJOR.MINOR.PATCH

* The first number, MAJOR, means non-backwards compatible changes like for
  example, required variables with data that cannot be patched in at a later
  stage.
* The second number, MINOR, means backwards compatible changes like for
  example, structural changes.
* The third number, PATCH, means backwards compatible changes like for
  example, name changes on variables.

NOTE: The backwards compatible versions, require conversion methods.

These conversion methods should be placed in the main-module, using the name
standard: 'update_OLD_to_NEW'
Where the version numbers have underscores instead of dots.
Example:

    def version_1_0_0_to_1_1_0(config):
        # --- Convert configuration here ---
        return convertedConfig

Examples of this can be found in the test suite.

"""

import re
import logging
import pkgutil
import pkg_resources
import importlib
import jsonschema
from jsonschema import ValidationError

import fw.uuid as uuid
import fw.cache as cache
import fw.file.tools as filetools
import fw.json.tools as jsontools

LOG = logging.getLogger(__name__)

_CONFIG_TYPES = {}
_CONFIGS_CACHE = {}
_SYSTEM_CONFIG_PATH = None


def get_config_types():
    """Function for fetching the dictionary containing config types."""
    return _CONFIG_TYPES


def remove_all_config_types():
    """Function for removing all loaded config types."""
    global _CONFIG_TYPES  # pylint: disable-msg=global-variable-not-assigned
    # Copy keys, to not corrupt iterator while looping and deleting.
    keys = list(_CONFIG_TYPES.keys())
    for key in keys:
        del _CONFIG_TYPES[key]


def get_configs_cache():
    """Function for fetching the dictionary containing all cached configs."""
    return _CONFIGS_CACHE


# def get_config(config_id):
#     config = _CONFIGS_CACHE.get(config_id)
#     if config is not None:
#         return config
#     return _load_config(config_id)


def load_config(config_path, get_latest=True):
    """Loads a json config from a file at the path.

    Returns the parsed json config object.
    The config is validated before it is returned and if that should fail,
    an exception is raised.

    """
    config = filetools.read_file(config_path)
    config_type, config_version, _ = get_config_api(config)
    if get_latest:  # No validation before update, to save performance.
        update_config(config)
    result = validate_config(config)
    if not result['status'] == 'ok':
        raise Exception((
                'Validation failed! Config type: {}, config version: '
                '{}. '.format(
                    config_type, config_version, result['error'][0].message
                )
            )
        )
    else:
        return config


def remove_all_configs_cache():
    """Function for removing all cached configs."""
    global _CONFIGS_CACHE  # pylint: disable-msg=global-variable-not-assigned
    # Copy keys, to not corrupt iterator while looping and deleting.
    keys = list(_CONFIGS_CACHE.keys())
    for key in keys:
        del _CONFIGS_CACHE[key]


def get_system_config_path():
    """Function for fetching the system config path."""
    return _SYSTEM_CONFIG_PATH


def set_system_config_path(path):
    """Function for setting the system config path."""
    global _SYSTEM_CONFIG_PATH  # pylint: disable-msg=global-statement
    _SYSTEM_CONFIG_PATH = path


def _extend_validator_with_defaults(validator_class):
    """Function that modifies the behavior of the Draft4Validator class.

    The modified behavior is used to set default values and build the default
    structure of the configuration, instead of validating the configuration.

    """
    def set_defaults(validator, properties, instance, schema):  # @IgnorePep8, pylint: disable-msg=W0613, C0301
        """Function for modifying the validator's behavior for default values.

        This function is injected into the Draft4Validator class.

        """
        if not validator.is_type(instance, 'object'):
            return

        for prop, subschema in properties.items():
            if 'default' in subschema.keys():
                instance.setdefault(prop, subschema['default'])
#             elif not 'type' in subschema.keys():
#                 for prop2, subschema2 in subschema.get('allOf', {}).keys():
#                     pass
#                 for prop2, subschema2 in subschema.get('anyOf', {}).keys():
#                     pass
#                 for prop2, subschema2 in subschema.get('oneOf', {}).keys():
#                     pass
            elif subschema['type'] == 'object':
                instance.setdefault(prop, {})
                for error in validator.descend(instance[prop], subschema,
                        path=prop, schema_path=prop):
                    yield error

    return jsonschema.validators.extend(
        validator_class, {
            'properties': set_defaults,
            'required': lambda param1, param2, param3, param4: None
        }
    )


def create_new_config(config_type, overrides=None, type_version='latest'):
    """Creates a new configuration, with default values and structure.

    Returns the config as a dictionary.
    The parameter 'overrides', provides

    """
    if not config_type in _CONFIG_TYPES.keys():
        raise KeyError('Config type "{}" not registered.'.format())
    if type_version == 'latest':
        versions = _CONFIG_TYPES[config_type]['schemas'].keys()
        versions = list(versions)  # To get an item that is indexable.
        type_version = get_latest_version(versions)
    schema = _CONFIG_TYPES[config_type]['schemas'][type_version]
    modified_validator = _extend_validator_with_defaults(
        jsonschema.Draft4Validator)
    base_config = {}
    modified_validator(schema).validate(base_config, schema)
    if overrides is None:
        overrides = {}
    if overrides.get('@config_id') is None:
        overrides['@config_id'] = uuid.get_unique_id()
    # Copy to avoid altering external dictionary.
    config = jsontools.deep_copy(overrides)
    jsontools.merge(config, base_config)
    result = validate_config(config)
    if result['status'] == 'error':
        raise result['errors'][0]
    return config


def get_latest_version(versions):
    """Compares a list of version strings and returns the latest version."""
    latest = None  # If there are no versions available.
    if len(versions) > 1:
        latest = '0.0.0'  # Start comparing against the absolute bottom.
        for index in range(len(versions)):
            version = pkg_resources.parse_version(versions[index])
            if version >= pkg_resources.parse_version(latest):
                latest = versions[index]  # Remember the highest version found.
            elif version < pkg_resources.parse_version(latest):
                continue
    elif len(versions) == 1:
        latest = versions[0]
    return latest


def get_config_versions(config_type):
    """Gets a sorted list of the versions of the specified config type."""
    keys = _CONFIG_TYPES.get(config_type, {}).get('schemas', {}).keys()
    keys = list(keys)
    keys.sort()
    return keys


def register_config_package(parent_package, include_names=None, prefix='cfg_'):
    """Registers all configurations within a Python package.

    If the parameter include_names contains a list of names, only those names
    will be registered (the names will be combined with the prefix).
    Example: include_names=['user_properties', 'customer_properties']

    """
    for package_info in pkgutil.walk_packages(parent_package.__path__):
        package_name = package_info[1]
        if package_name.startswith(prefix) and not '.' in package_name:
            full_package_name = '{}.{}'.format(parent_package.__name__,
                package_name)
            cfg_package = importlib.import_module(full_package_name)
            config_info = _get_config_info(cfg_package)
            if include_names and not config_info['type'] in include_names:
                continue  # Skip packages not in include_names.
            _CONFIG_TYPES[config_info['type']] = config_info


def get_config_api(config):
    """Returns a tuple, (config_type, config_version, config_prev_version)."""
    return (
        config['@api']['name'],
        config['@api']['version'],
        config['@api']['prev_version'],
    )


def _get_config_info(cfg_package):
    """Fetches the configuration package information from it's modules.

    The config information is collected in a dictionary, containing the
    config type name, a dictionary containing its schemas and any update
    methods found in the configurations main module.
    Example:

    {
        "type": "MyCustomConfig",
        "schemas": {
            "1.0.0": {...schema...},
            "1.1.0": {...schema...}
        },
        "updates": {
            "1.0.0-1.1.0": <function pointer>
        }
    }

    """
    config_info = {'schemas': {}}
    base_name = cfg_package.__name__
    for package_info in pkgutil.walk_packages(cfg_package.__path__):
        package_name = package_info[1]
        if package_name.startswith('main'):
            main_name = '{}.{}'.format(base_name, 'main')
            main = importlib.import_module(main_name)
            config_info['type'] = main.CONFIG_TYPE
            for key, value in main.__dict__.items():
                if key.startswith('update_'):
                    updates = config_info.get('updates', {})
                    version_key = key.replace('update_', '').replace(
                        '_to_', '-').replace('_', '.')
                    updates[version_key] = value
                    config_info['updates'] = updates
        elif package_name.startswith('schema_'):
            schema_name = '{}.{}'.format(base_name, package_name)
            schema = importlib.import_module(schema_name)
            schema_version = package_name.replace('schema_', '').replace(
                '_', '.')
            config_info['schemas'][schema_version] = schema.CONFIG_SCHEMA
    return config_info


def validate_config(config):
    """Validates a config with the configuration version's specified schema."""
    error_dict = _validate_config_api(config)
    if len(error_dict['errors']) > 0:
        return error_dict
    config_type, config_version, _ = get_config_api(config)
    schema = _CONFIG_TYPES[config_type]['schemas'][config_version]
    validator = jsonschema.Draft4Validator(schema)
    errors = sorted(validator.iter_errors(config), key=lambda e: e.path)
    if errors:
        error_dict['errors'] = errors
    else:
        error_dict['status'] = 'ok'
    return error_dict


def _validate_config_api(config):
    """Sub method to validate the api section of a config."""
    error_dict = {
        'status': 'error',
        'errors': []
    }
    config_type = config.get('@api', {}).get('name')
    if not config_type:
        error_dict['errors'].append(_get_validation_error(
            'Config api type name missing.'))
        return error_dict
    if not config_type in _CONFIG_TYPES.keys():
        error_dict['errors'].append(_get_validation_error(
            'Config api type not registered: "{}"', config_type))
        return error_dict
    config_version = config.get('@api', {}).get('version')
    if not config_version:
        error_dict['errors'].append(_get_validation_error(
            'Config api version missing.'))
        return error_dict
    if not re.match('^(\\d+\\.)(\\d+\\.)(\\d+)$', config_version):
        error_dict['errors'].append(_get_validation_error(
            'Illegally formatted config api version: "{}"',
                config_version))
    previous_version = config.get('@api', {}).get('prev_version', '')
    if previous_version == '':
        error_dict['errors'].append(_get_validation_error(
            'Config api previous version missing.'))
    if previous_version != None:
        if not re.match('^(\\d+\\.)(\\d+\\.)(\\d+)$', previous_version):
            error_dict['errors'].append(_get_validation_error(
                'Illegally formatted config api previous version: "{}"',
                previous_version))
            return error_dict
    config_info = _CONFIG_TYPES[config_type]
    if not config_version in config_info.get('schemas', {}).keys():
        error_dict['errors'].append(_get_validation_error(
            'Config api version not registered: "{}"', config_version))
    return error_dict


def _get_validation_error(message, variable=None):
    """Create and return a jsonschema validation error."""
    if variable is not None:
        message = message.format(variable)
    return ValidationError(message)


def get_version_chain(config_type, target_version, latest_version):
    """Builds a list of pairs of configuration versions.

    Returns a list of tuples. Each version number pair, represent the versions
    between which a conversion method needs to be called.
    If the version is already at the latest version, an empty list is returned.
    Example of return data:

    [('1.0.0', '1.0.1'), ('1.0.1', '1.1.0')]

    """
    chain = []
    if target_version == latest_version:
        return chain
    latest_schema = _CONFIG_TYPES[config_type]['schemas'][latest_version]
    previous_version = latest_schema['properties']['@api']['properties'][
        'prev_version']['default']
    if previous_version != None:
        if previous_version != target_version:
            _get_version_chain(config_type, target_version, previous_version,
                chain)
        chain.append((previous_version, latest_version))
    return chain


def _get_version_chain(config_type, target_version, current_version, chain):
    """Recursive sub method to the method get_version_chain."""
    current_schema = _CONFIG_TYPES[config_type]['schemas'][current_version]
    previous_version = current_schema['properties']['@api']['properties'][
        'prev_version']['default']
    if previous_version != None:
        if previous_version != target_version:
            _get_version_chain(config_type, target_version, previous_version,
                chain)
        chain.append((previous_version, current_version))
    return


def _apply_config_updates(config, version_chain):
    """Applies all update functions for each version step in the chain."""
    config_type = config['@api']['name']
    for previous_version, next_version in version_chain:
        conversion_key = '{prev}-{next}'.format(prev=previous_version,
            next=next_version)
        updates = _CONFIG_TYPES[config_type].get('updates', {})
        if not conversion_key in updates.keys():
            raise KeyError('Conversion method missing for versions {}'.format(
                conversion_key))
        update_method = updates[conversion_key]
        config = update_method(config)
    return config


def update_config(config, version_chain=None):
    """Updates a config, one version step at a time.

    A version chain can be specified, but it is primarily intended for testing.
    Nothing is returned, since the config object is modified directly.

    """
    config_type, config_version, _ = get_config_api(config)
    try:
        if version_chain is None:
            versions = get_config_versions(config_type)
            latest = get_latest_version(versions)
            version_chain = get_version_chain(config_type, config_version,
                latest)
            if latest == config_version:
                return config
        _apply_config_updates(config, version_chain)
    except KeyError as exc:
        message = (
            'Config update failed! Config type: {}, '
            'config version: {}.'
        ).format(config_type, config_version)
        raise Exception(message) from exc
    except Exception as exc:
        result = validate_config(config)
        message = (
            'Config update failed! Config type: {}, '
            'config version: {}.'
        ).format(config_type, config_version)
        if not result['status'] == 'ok':
            message = '{} Validation also failed: {}.'.format(message,
                result['error'][0].message)
        raise Exception(message) from exc


def register_wsgi_apps_types(types):
    """Registers custom wsgi application types."""
    apps_types = cache.get_wsgi_apps_types()
    for type_name, type_value in types.items():
        if type_name in apps_types.keys():
            LOG.warning(
                'Registering already existing wsgi apps type "{}".'.format(
                    type_name))
        apps_types[type_name] = type_value


def get_app_config(parts):
    return parts
