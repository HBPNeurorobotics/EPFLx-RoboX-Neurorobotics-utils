import setuptools
import os
from optparse import Option
import pip

def parse_reqs(reqs_file):
    ''' parse the requirements '''
    options = Option("--workaround")
    options.skip_requirements_regex = None
    # Hack for old pip versions
    major = int(pip.__version__.split('.')[0])
    if major >= 10:
        # Versions greater or equal to 10.x don't rely on pip.req.parse_requirements
        install_reqs = list(val.strip() for val in open(reqs_file))
        reqs = install_reqs
    elif major ==  1:
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
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="epflx_robox_nrp_utils",
    version="0.0.1",
    author="Ihor Kuras",
    author_email="ihor.kuras@epfl.ch",
    description="Functions and classes for SOM and SARSA algorithms (EPFLx-Robox-Neurorobotics)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HBPNeurorobotics/EPFLx-RoboX-Neurorobotics-utils",
    packages=setuptools.find_packages(),
    install_requires=REQS,
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
