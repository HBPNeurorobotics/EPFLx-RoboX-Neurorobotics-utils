# ---LICENSE-BEGIN - DO NOT CHANGE OR MOVE THIS HEADER
# This file is part of the Neurorobotics Platform software
# Copyright (C) 2014,2015,2016,2017 Human Brain Project
# https://www.humanbrainproject.eu
#
# The Human Brain Project is a European Commission funded project
# in the frame of the Horizon2020 FET Flagship plan.
# http://ec.europa.eu/programmes/horizon2020/en/h2020-section/fet-flagships
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# ---LICENSE-END
"""
A strongly validated configuration implementation for the VirtualCoach.
"""

import json
import logging
import os

logger = logging.getLogger('Configuration')


class Config(dict):
    """
    A configuration object that validates configuration file contents to ensure all necessary
    parameters are defined.
    """

    def __init__(self, environment):
        """
        Load and validate the configuration file. Update all proxy service parameters to use
        the given environment.

        :param environment A string for the environment to be used (e.g. 'production', 'dev',
                           'local', or a custom value defined in the config.json).
        """

        # initialize the parent dictionary, required by pylint
        dict.__init__(self)

        # ensure the config.json file exists and is readable by our user
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')
        if not os.path.isfile(path):
            raise IOError('[config] config.json not found, terminating.')
        elif not os.access(path, os.R_OK):
            raise IOError('[config] config.json is not readable, terminating.')

        # parse the config.json and store all values in this object
        with open(path) as conf_file:
            try:
                conf = json.load(conf_file)
            except Exception as e:
                raise IOError('[config] Malformed config.json: %s' % str(e))

            self.update(conf)

        if environment in ['local', 'dev', 'staging']:
            self.update({'environment': environment })
        elif environment is not None:
          raise ValueError('[config] Invalid argument: environment should be local, dev or staging')

        # validate required sections of the config, except if any values are missing
        self.__validate('oidc', ['user'])
        self.__validate('grading-server', ['staging', 'dev', 'local'])
        self.__validate('submission-header', [])
        self.__validate('environment', [])

    def __validate(self, key, values):
        """
        Internal helper to validate that a key with given list of values/sub-keys is
        present in the config. Raise an exception if the key or any values are missing.

        :param key A string representing the high level group to check for in the config.
        :param values A list of sub-keys to check under the parent key.
        """

        if key not in self:
            raise KeyError('[config] Invalid or obsolete, missing section: %s' % key)

        for value in values:
            if value not in self[key]:
                raise ValueError('[config] Invalid or obsolete, missing value %s in section %s' %
                                 (value, key))
