## Setup in your package

Create a default/sample `settings.ini` file in the module directory of your
package, with a `[default]` section and any other `[sections]` you want (i.e.
app environments)

```
[default]
something = 100

[dev]
redis_url = redis://localhost:6379/1
something = 500

[test]
redis_url = redis://localhost:6379/9
things = none, true, false, 1, 2.5, dogs
```

Create a `MANIFEST.in` file in your package directory with the following

```
include settings.ini
```

Update the `setup.py` file of the package to include the `setting.ini` file and
add `settings-helper` to `install_requires` list

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

## Usage

Use in `__init__.py` of package

```
import settings_helper as sh

get_setting = sh.settings_getter(__name__)
something = get_setting('something')
something_else = get_setting('something_else', 'default_val')
```

Set `APP_ENV` environment variable to be one of your section names when starting
your Python interpreter/server. **`APP_ENV` defaults to `dev` if it is not set.**

- The `get_setting` func will return the value of the requested variable if it
  is set in the section specified in `APP_ENV`.
- If the variable is not in the section, it will pull the value from the
  `[default]` section
- If the varialbe is not in the `[default]` section either, then return the
  optional fallback value passed in the `default` keyword argument to
  `get_setting` (which defaults to an empty string)
- **If the requested variable exists in the environment (or its uppercase
  equivalent), it will be used instead of getting from settings.ini**
- The value is automatically converted to a bool, None, int, or float if it
  should be
- If the value contains any of (, ; |) then a list of converted values will be
  returned

The first time that `settings_getter` func is invoked, it looks for a
`settings.ini` file in `~/.config/<package-name>/settings.ini`.

- If it does not find it, it will copy the default settings.ini from the
  module's install directory to that location
- If the settings.ini file does not exist in the module's install directory, an
  exception is raised

## Alternate Usage

```
import settings_helper as sh

settings = sh.get_all_settings(__name__)
```

or

```
import settings_helper as sh

settings = sh.get_all_settings(__name__).get(sh.APP_ENV, {})
```

The `get_all_settings` func returns a dict containing all sections other than
'default'.

- If a setting is defined in 'default', but not in a particular section, the
  setting in 'default' will appear under the section
- If a setting (or upper-case equivalent) is defined as an environment variable,
  that value will be used for all sections that use it

## Tip

In your `<package-name>/tests/__init__.py` file, add the following so the `test`
section of settings is automatically used

```
import os

os.environ['APP_ENV'] = 'test'
```
