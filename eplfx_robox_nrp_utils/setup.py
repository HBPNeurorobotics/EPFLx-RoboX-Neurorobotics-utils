'''setup.py'''
# pylint: disable=R0801
import os

from setuptools import setup
from optparse import Option

import epflx_robox_nrp_utils
import pip


def parse_reqs(reqs_file):
    ''' parse the requirements '''
    options = Option("--workaround")
    options.skip_requirements_regex = None
    # Hack for old pip versions
    if pip.__version__.startswith('10.'):
        # Versions greater or equal to 10.x don't rely on pip.req.parse_requirements
        install_reqs = list(val.strip() for val in open(reqs_file))
        reqs = install_reqs
    elif pip.__version__.startswith('1.'):
        # Versions 1.x rely on pip.req.parse_requirements
        # but don't require a "session" parameter
        from pip.req import parse_requirements # pylint:disable=no-name-in-module, import-error
        install_reqs = parse_requirements(reqs_file, options=options)
        reqs = [str(ir.req) for ir in install_reqs]
    else:
        # Versions greater than 1.x but smaller than 10.x rely on pip.req.parse_requirements
        # and requires a "session" parameter
        from pip.req import parse_requirements # pylint:disable=no-name-in-module, import-error
        from pip.download import PipSession  # pylint:disable=no-name-in-module, import-error
        options.isolated_mode = False
        install_reqs = parse_requirements(  # pylint:disable=unexpected-keyword-arg
            reqs_file,
            session=PipSession,
            options=options
        )
        reqs = [str(ir.req) for ir in install_reqs]
    return reqs


BASEDIR = os.path.dirname(os.path.abspath(__file__))
REQS = parse_reqs(os.path.join(BASEDIR, 'requirements.txt'))

EXTRA_REQS_PREFIX = 'requirements_'
EXTRA_REQS = {}
for file_name in os.listdir(BASEDIR):
    if not file_name.startswith(EXTRA_REQS_PREFIX):
        continue
    base_name = os.path.basename(file_name)
    (extra, _) = os.path.splitext(base_name)
    extra = extra[len(EXTRA_REQS_PREFIX):]
    EXTRA_REQS[extra] = parse_reqs(file_name)

config = {
    'description': 'Functions for the implementation of the SOM and SARSA algorithms (EPFL NRP MOOC)',
    'author': 'HBP neurorobotics',
    'url': 'http://neurorobotics.net',
    'author_email': 'neurorobotics@humanbrainproject.eu',
    'version': epflx_robox_nrp_utils.__version__,
    'install_requires': REQS,
    'extras_require': EXTRA_REQS,
    'packages': ['epflx_robox_nrp_utils.',
                 'epflx_robox_nrp_utils.SARSA', 'epflx_robox_nrp_utils.SOM'],
    'scripts': [],
    'name': 'epflx-robox-nrp-utils',
    'include_package_data': True,
}

setup(**config)
