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
Functions dedicated the susbmission process of users'answers to the grading server
"""

from config import Config
from oidc_http_client import OIDCHTTPClient

from datetime import datetime, timedelta
from dateutil import parser, tz
import json
import requests
import logging
import getpass

logger_format = '%(levelname)s: [%(asctime)s - %(name)s] %(message)s'
logging.basicConfig(format=logger_format, level=logging.INFO)
logger = logging.getLogger('SubmissionManager')


class SubmissionManager(object):
    """
    Handles the submission of user's solution to the NRP MOOC grading server 
    """

    def __init__(self, oidc_username='', token=''):
        """
        

        :param oidc_username: (optional) A string representing the OIDC username
                              Required for OIDC authentication if no token is provided. 
                              The user will be interactively 
                              asked for a password by the OIDC client if the token has expired 
                              or if they have not logged in.

        :param token: (optional) A string representing the OIDC token of the current user
                              
        """
        assert isinstance(oidc_username, (str))
        assert isinstance(token, (str))
        # Parse and load the config file before any OIDC actions
        self.__config = Config()
        self.__oidc_username = oidc_username
        self.__token = token
        if self.__token or self.__oidc_username:
            # This will interactively prompt the user for a password in terminal if needed
            logger.info('Logging into OIDC as: %s', self.__oidc_username)
            self.__http_client = OIDCHTTPClient(
                oidc_username=self.__oidc_username, token=self.__token
            )

            authorization = self.__http_client.get_auth_header()
            self.__http_headers = {'Content-Type': 'application/json',
                                    'Authorization': authorization}
            self.__http_client.set_headers(self.__http_headers)
        else:
            raise Exception('No valid credentials - Submission failed.')

        # If the config is valid and the login doesn't fail, we're ready
        logger.info('Ready to submit.')


    def submit(self):
        body = self.create_submission_form()
        environment = self.__config['environment']
        status_code, content = self.__http_client.post(self.__config['grading-server'][environment], body=body)
        if status_code != 200:
            raise Exception('Submission failed, Status Code: %s' % status_code)
        else:
            logger.info('Successful submission!')
            
    
    def create_submission_form(self):
        submission_form = { "submissionInfo": self.__config['submission-header'], 
          "answer": "167",
          "fileName": "solution.py",
          "fileContent": "AAASSXCEEERRFRF"
        }
        return submission_form        
