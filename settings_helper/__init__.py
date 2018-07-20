import configparser
import os.path
import input_helper as ih
from os import getenv, makedirs
from shutil import copyfile


APP_ENV = getenv('APP_ENV', 'dev')


def _get_settings_file(module_name):
    package_name = module_name.replace('_', '-')
    home_config_dir = os.path.expanduser('~/.config/{}'.format(package_name))
    this_dir = os.path.abspath(os.path.dirname(__file__))
    install_dir = os.path.dirname(this_dir)
    module_install_dir = os.path.join(install_dir, module_name)
    settings_file = os.path.join(home_config_dir, 'settings.ini')
    if not os.path.isfile(settings_file):
        default_settings = os.path.join(module_install_dir, 'settings.ini')
        if not os.path.isfile(default_settings):
            raise Exception('No default {} found... not able to create {}'.format(
                repr(default_settings), repr(settings_file)
            ))
        try:
            makedirs(home_config_dir)
        except FileExistsError:
            pass
        print('copying {} -> {}'.format(repr(default_settings), repr(settings_file)))
        copyfile(default_settings, settings_file)

    return settings_file


def _get_config_object(module_name):
    settings_file = _get_settings_file(module_name)
    config = configparser.RawConfigParser()
    config.read(settings_file)
    return config


def settings_getter(module_name):
    """Return a 'get_setting' func to get a setting from settings.ini for a section"""
    config_object = _get_config_object(module_name)

    def get_setting(name, default='', section=APP_ENV, config_object=config_object):
        """Get a setting from settings.ini for a particular section (or env var)

        If an environment variable of the same name (or ALL CAPS) exists, return it.
        If item is not found in the section, look for it in the 'default' section.
        If item is not found in the default section of settings.ini, return the
        default value

        The value is converted to a bool, None, int, float if it should be.
        If the value contains any of (, ; |), then the value returned will
        be a list of items converted to (bool, None, int, float, or str).
        """
        val = getenv(name, getenv(name.upper()))
        if not val:
            try:
                val = config_object[section][name]
            except KeyError:
                try:
                    val = config_object['default'][name]
                except KeyError:
                    return default
                else:
                    val = ih.from_string(val)
            else:
                val = ih.from_string(val)
        else:
            val = ih.from_string(val)

        if type(val) == str and (',' in val or ';' in val or '|' in val):
            val = list(map(ih.from_string, ih.string_to_list(val)))
        return val

    return get_setting
