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
Functions dedicated to the susbmission process of users'answers to the grading server
"""

from config import Config
from oidc_http_client import OIDCHTTPClient
import json
import requests
import logging
import os
import signal

logger_format = '%(levelname)s: [%(asctime)s - %(name)s] %(message)s'
logging.basicConfig(format=logger_format, level=logging.INFO)
logger = logging.getLogger('SubmissionManager')


class TimeoutException(Exception):
    pass


def check_submission_info(submission_info):
    assert isinstance(submission_info, (dict))
    assert isinstance(submission_info['token'], (str))
    assert isinstance(submission_info['filepath'], (str))
    assert isinstance(submission_info['collab_path'], (str))
    
    no_oidc_username = 'oidc_username' not in submission_info or not submission_info['oidc_username']
    no_token = 'token' not in submission_info or not submission_info['token']
    if no_oidc_username and no_token:
        raise ValueError(
            "You need to specify either " 
            "an oidc_username or a token in order to submit your answer."
        )

    if not os.path.exists(submission_info['filepath']):
        error_msg = '(Error message) File not found: the file named %(filepath)s does not exist' % \
            {'filepath': submission_info['filepath']}
        raise Exception('Submission failed! \n %(error_msg)s' % {'error_msg': error_msg})


class SubmissionManager(object):
    """
    Handles the submission of user's solution to the NRP MOOC grading server
    """

    """
    :param submission_info:  A dictionary with the following keys:
                            subheader, oidc_username (optional), token, filepath, collab_path and
                            clients_storage.
                            subheader is a string describing the submission context, e.g., 'Exercise 3'
                            oidc_username is a string containing the HBP OIDC username (optional)
                            token is a string containing the HBP OIDC token of the user
                            filepath is a string containing the name of the submitted file
                            collab_path is the path to the HBP Collab where the submission takes place
                            clients_storage is an object with a download_file method, e.g, clients.storage from bbp_services

    """
    def __init__(self, submission_info):
        # Parse and load the config file before any OIDC actions
        self.__config = Config()
        check_submission_info(submission_info)
        self.__submission_info = submission_info
        self.__timeout = 240
        if 'token' in self.__submission_info or 'oidc_username' in self.__submission_info:
            oidc_username=''
            token=''
            # This will interactively prompt the user for a password in terminal if needed
            if 'oidc_username' in self.__submission_info:
                logger.info('Logging into OIDC as: %s', self.__submission_info['oidc_username'])
                oidc_username=self.__submission_info['oidc_username'] 
            if 'token' in self.__submission_info:
                token = self.__submission_info['token']
            self.__http_client = OIDCHTTPClient(
                oidc_username=oidc_username, 
                token=token
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
        self.init_grading_functions()

    def init_grading_functions(self):
        filepath = self.__submission_info['filepath']

        def grade_SOM():
            from epflx_robox_nrp_utils.grading.SOM_autograding import SOM_autograding
            som = SOM_autograding()
            self.__score = som.grade_one_function(filepath)

        def grade_SARSA():
            from epflx_robox_nrp_utils.grading.SARSA_autograding import SARSA_autograding
            sarsa = SARSA_autograding()
            self.__score = sarsa.grade_one_function(filepath)

        def timeoutHandler():
            raise TimeoutException()


        self.__grading_functions = {'Exercise 2': grade_SOM, 'Exercise 3': grade_SARSA}
        signal.signal(signal.SIGALRM, timeoutHandler)

    def grade(self):
        grading_function = self.__grading_functions[self.__submission_info['subheader']]
        signal.alarm(self.__timeout)
        grading_function()

    def submit(self):
        try: # try grading
            self.grade()
        except TimeoutException:
            print('Submission Timeout: the time to execute %(filepath)s exceeds %(timeout)d minutes' % 
                { 'filepath': self.__submission_info['filepath'], 'timeout': self.__timeout / 60 }
            )
            raise Exception('Submission failed.')
        except Exception as e:
            print('Python error when executing %(filepath)s' % {'filepath': self.__submission_info['filepath']})
            print('Submission failed because of an error raised by your code.'
                'Please test and fix your code before your next submission.'
            )
            raise e
        
        # submit answer to a database
        body = self.create_submission_form()
        environment = self.__config['environment']
        status_code, content = self.__http_client.post(self.__config['grading-server'][environment], body=body)
        if status_code != 200:
            raise Exception('Submission failed, Status Code: %s' % status_code)
        else:
            logger.info('Congratulations, your submission is successful!')

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
            submission_form['answer'][str(i + 1)] = self.__score[i]
        return submission_form
