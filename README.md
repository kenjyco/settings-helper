Environment-aware configuration management for Python packages using INI files with automatic type conversion to basic types (int, float, None, bool, str). Any variables with multiple comma-separated values will be converted to a list. Handles multi-environment setups (i.e. dev/testing) with automatic file discovery across standard configuration locations. **Environment variables override INI values** (i.e. prod) when they have the same name (or UPPERCASE name) as variables in the `settings.ini` file. You can comment out any variables in the settings.ini file with a leading `#`.

## Example settings.ini

```ini
[default]
something = 100
# other = 250

[dev]
redis_url = redis://localhost:6379/1
something = 500

[test]
redis_url = redis://localhost:6379/9
things = none, true, false, 1, 2.5, dogs
something_else = 2.0
```

Searches `~/.config/<package>/settings.ini`, `/etc/<package>/settings.ini`, `/tmp/<package>/settings.ini`, then `./settings.ini`. Copies default settings from package if missing. See [Setup in your package](https://github.com/kenjyco/settings-helper/blob/master/README.md#setup-in-your-package) below to define a default settings.ini file for your package.

You must include at least one section header in your settings.ini file (like `[default]`). The configparser will raise a MissingSectionHeaderError if no headers are defined. The only special header is **`[default]`**. If you have any additional section headers, each parsed section will only contain things defined in that section, plus anything defined in the `[default]` section.

## Install

```
pip install settings-helper
```

## QuickStart

```python
import settings_helper as sh

# Get all settings by section
settings = sh.get_all_settings(__name__)
# Returns:
# {
#     'default': {'something': 100},
#     'dev': {'redis_url': 'redis://localhost:6379/1', 'something': 500},
#     'test': {'redis_url': 'redis://localhost:6379/9', 'something': 100, 'something_else': 2.0,
#              'things': [None, True, False, 1, 2.5, 'dogs']}
# }

# Get environment-specific settings (APP_ENV defaults to 'dev')
SETTINGS = sh.get_all_settings(__name__).get(sh.APP_ENV, {})
redis_url = SETTINGS.get('redis_url')
something = SETTINGS.get('something', 100)

# Alternative: use settings getter factory
get_setting = sh.settings_getter(__name__)
redis_url = get_setting('redis_url')
something = get_setting('something', 100)

# All values are automatically converted: 'true' → True, '100' → 100, 'none' → None
# Lists are automatically parsed: 'a,b,c' → ['a', 'b', 'c']
```

Note that when using the older `settings_getter`, the **`APP_ENV`** environment variable is used to determine the section of the setttings.ini file to get the value from. This value defaults to `dev` if not set. If the variable is not defined in the section, it will pull the value from the `[default]` section. If the variable is not defined in the default section, it will return the optional fallback value.

## Setup for a one-off script

Create a `settings.ini` file next to your script with at least one section header in square brackets (like `[my stuff]`).

```
[my stuff]
something = 100
things = none, true, false, 1, 2.5, dogs and cats, grapes
# other = 500
```

Use the simple `get_all_settings` function to get a dict of all settings by section header.

```
import settings_helper as sh

settings = sh.get_all_settings()
```

For our settings.ini file example, the settings dict from `get_all_settings()` would be the following:

```
{
    'my stuff': {
        'something': 100,
        'things': [None, True, False, 1, 2.5, 'dogs and cats', 'grapes']
    }
}
```

When dealing with settings where values are numbers, but you don't want them converted (i.e. version numbers like "3.10"), you can set kwarg `keep_num_as_string` to `True` when calling `get_all_settings` (or `settings_getter`).

```
import settings_helper as sh

settings = sh.get_all_settings(keep_num_as_string=True)
```

For our settings.ini file example, the settings dict from `get_all_settings(keep_num_as_string=True)` would be the following:

```
{
    'my stuff': {
        'something': '100',
        'things': [None, True, False, '1', '2.5', 'dogs and cats', 'grapes']
    }
}
```

## Setup in your package

Create a default/sample `settings.ini` file in the module directory of your package, with a `[default]` section and any other `[sections]` you want (i.e. app environments)

```
[default]
something = 100

[dev]
redis_url = redis://localhost:6379/1
something = 500

[test]
redis_url = redis://localhost:6379/9
things = none, true, false, 1, 2.5, dogs
something_else = 2.0
```

For this settings.ini file example, the settings dict from `get_all_settings()` would be the following:

```
{
    'dev': {
        'something': 500,
        'redis_url': 'redis://localhost:6379/1'
    },
    'default': {
        'something': 100
    },
    'test': {
        'something': 100,
        'something_else': 2.0,
        'redis_url': 'redis://localhost:6379/9',
        'things': [None, True, False, 1, 2.5, 'dogs']
    }
}
```

Create a `MANIFEST.in` file in your package directory with the following

```
include settings.ini
```

Update the `setup.py` file of the package to include the `setting.ini` file and add `settings-helper` to `install_requires` list

```
from setuptools import setup, find_packages

setup(
    name='package-name',
    version='0.0.1',
    ...
    packages=find_packages(),
    install_requires=[
        'settings-helper',
        ...
    ],
    include_package_data=True,
    package_dir={'': '.'},
    package_data={
        '': ['*.ini'],
    },
    ...
)
```

Note, your package directory tree will be something like the following

```
package-name
├── .gitignore
├── LICENSE.txt
├── MANIFEST.in
├── README.md
├── README.rst
├── package_name/
│   ├── __init__.py
│   └── settings.ini
└── setup.py
```

### Tip

In your `<package-name>/tests/__init__.py` file, add the following so the `test`
section of settings is automatically used

```
import os

os.environ['APP_ENV'] = 'test'
```

## API Overview

### Configuration Loading

- **`get_all_settings(module_name='', keep_num_as_string=False)`** - Return all settings by section
  - `module_name`: Package name for settings discovery
  - `keep_num_as_string`: Preserve numeric strings without conversion
  - Returns: Dictionary with section names as keys
  - Internal calls: `ih.from_string()`, `ih.string_to_converted_list()`

- **`settings_getter(module_name, section=APP_ENV, keep_num_as_string=False)`** - Create setting getter function
  - `module_name`: Package name for settings discovery
  - `section`: Configuration section to use
  - `keep_num_as_string`: Preserve numeric strings without conversion
  - Returns: Function for retrieving individual settings
  - Internal calls: None

### File Management

- **`get_settings_file(module_name='', copy_default_if_missing=True, exception=True)`** - Locate settings file
  - `module_name`: Package name for discovery (empty for current directory)
  - `copy_default_if_missing`: Copy default settings if missing
  - `exception`: Raise exception if not found
  - Returns: Path to settings.ini file
  - Internal calls: `get_default_settings_file()`

- **`get_default_settings_file(module_name, exception=True)`** - Find package default settings
  - `module_name`: Package name to search
  - `exception`: Raise exception if not found
  - Returns: Path to default settings.ini in package
  - Internal calls: None

- **`sync_settings_file(module_name)`** - Compare settings with vimdiff
  - `module_name`: Package name
  - Returns: None (launches vimdiff if files differ)
  - Internal calls: `get_settings_file()`, `get_default_settings_file()`, `bh.run_output()`, `bh.run()`
