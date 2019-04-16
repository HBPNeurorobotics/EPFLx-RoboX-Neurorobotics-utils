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
Submission widgets displayed in a Jupyter notebook
"""



import logging
import ipywidgets as widgets
from IPython.display import clear_output
from IPython.display import display
from os import path
import time
from epflx_robox_nrp_utils.submission_manager.submit_answer import SubmissionManager

logger_format = '%(levelname)s: [%(asctime)s - %(name)s] %(message)s'
logging.basicConfig(format=logger_format, level=logging.INFO)
logger = logging.getLogger('submission_widget')


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
def display_submission_widget(submission_info):
    filepath_widget = widgets.Text(
        description='File path', 
        placeholder='Python file path, e.g., %(filepath)s' % {'filepath': submission_info['filepath']},
        layout=widgets.Layout(width='50%')
    )
    display(filepath_widget)
    submission_button = widgets.Button(
        description="Submit", 
        layout=widgets.Layout(width='50%', height='35px')
    )
    display(submission_button)


    def button_callback(submission_info):
        def on_button_clicked(b):
            sm = SubmissionManager(submission_info)
            clear_output()
            filepath = str(filepath_widget.value) if filepath_widget.value else submission_info['filepath']
            print("Downloading %(filepath)s to your Jupyter user space ..." % {'filepath': filepath})
            submission_info['clients_storage'].download_file(
                path.join(submission_info['collab_path'], filepath), 
                submission_info['filepath']
            )
            submission_button.close()
            filepath_widget.close()
            time.sleep(3)
            clear_output()
            sm.submit()
        return on_button_clicked
        

    submission_button.on_click(
        button_callback(submission_info)
    )