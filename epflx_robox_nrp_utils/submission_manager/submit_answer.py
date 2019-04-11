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
import json
import requests
import logging
import os

logger_format = '%(levelname)s: [%(asctime)s - %(name)s] %(message)s'
logging.basicConfig(format=logger_format, level=logging.INFO)
logger = logging.getLogger('SubmissionManager')


class TimeoutException(Exception):
    pass


class SubmissionManager(object):
    """
    Handles the submission of user's solution to the NRP MOOC grading server
    """

    def __init__(self, oidc_username='', token='', submission_info=None):
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
        assert isinstance(submission_info, (dict))
        if os.path.exist(self.__submission_info['filepath']) is False:
            print 'File not found: %(filepath)s does not exist' % {'filepath': self.__submission_info['filepath']}
            raise Exception('Submission failed.')
        # Parse and load the config file before any OIDC actions
        self.__config = Config()
        self.__oidc_username = oidc_username
        self.__token = token
        self.__submission_info = submission_info
        self.__timeout = 260
        if self.__token or self.__oidc_username:
            # This will interactively prompt the user for a password in terminal if needed
            if self.__oidc_username:
                logger.info('Logging into OIDC as: %s', self.__oidc_username)
            self.__http_client = OIDCHTTPClient(
                oidc_username=self.__oidc_username, token=self.__token
            )
            authorization = self.__http_client.get_auth_header()
            self.__http_headers = {
                'Content-Type': 'application/json',
                'Authorization': authorization
            }
            self.__http_client.set_headers(self.__http_headers)
        else:
            raise Exception('No valid credentials - Submission failed.')

        # If the config is valid and the login doesn't fail, we're ready
        logger.info('Ready to submit.')
        init_grading_functions()
        try:
            grade()
        except TimeoutException:
            print 'Submission Timeout: the time to execute %(filepath)s exceeds %(timeout)d minutes' % \ 
                { 'filepath': self.__submission_info['filepath'], 'timeout': self.__timeout / 60 }
            raise Exception('Submission failed.')
        except as e:
            print 'Python error when executing %(filepath)s' % {'filepath': self.__submission_info['filepath']}
            print 'Submission failed because of an error raised by your code.'
                'Please test and fix your code before your next submission.'
            raise e
        submit()

    def init_grading_functions(self):
        filepath = self.__submission_info['filepath']

        def grade_SOM():
            from epflx_robox_nrp_utils.graduation.SOM_autograduation import SOM_autograduation
            som = SOM_autograduation()
            self.__score = som.graduate_one_function(filepath)

        def grade_SARSA():
            from epflx_robox_nrp_utils.graduation.SARSA_autograduation import SARSA_autograduation
            sarsa = SARSA_autograduation()
            self.__score = sarsa.graduate_one_function(filepath)

        def timeoutHandler():
            raise TimeoutException()


        self.__grading_functions = {'Exercise 2': grade_SOM, 'Exercise 3': grade_SARSA}
        signal.signal(signal.SIGALRM, timeoutHandler)

    def grade(self):
        grading_function = self.__graduation_functions[self.__submission_info['subheader']]
        signal.alarm(self.__timeout)
        grading_function()

    def submit(self):
        body = self.create_submission_form()
        environment = self.__config['environment']
        status_code, content = self.__http_client.post(self.__config['grading-server'][environment], body=body)
        if status_code != 200:
            raise Exception('Submission failed, Status Code: %s' % status_code)
        else:
            logger.info('Successful submission!')

    def create_submission_form(self):
        with open(self.__submission_info['filepath'], 'r') as submitted_file:
            file_str = submitted_file.read()
        submission_form = {
            "submissionInfo": {
                'header': self.__config['submission-header'],
                'subheader': self.__submission_info['subheader']
            },
            'fileName': os.path.basename(self.__submission_info['filepath']),
            'fileContent': file_str
        }
        submission_form['answer'] = dict()
        for i in range(0, 3):
            submission_header['answer'][str(i + 1)] = self.__score[i]
        return submission_form
