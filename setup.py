# Copyright (C) 2022 Geovane Fedrecheski <geonnave@gmail.com>
#               2022 Universidade de São Paulo
#               2022 LSI-TEC

# This file is part of the SwarmOS project, and it is subject to
# the terms and conditions of the GNU Lesser General Public License v2.1.
# See the file LICENSE in the top level directory for more details.

from setuptools import find_packages, setup, os

def _read_requirements(file_name):
    """
    Returns list of required modules for 'install_requires' parameter. Assumes
    requirements file contains only module lines and comments.
    """
    requirements = []
    with open(os.path.join(file_name)) as f:
        for line in f:
            if not line.startswith('#') and not line.startswith('git'):
                requirements.append(line)
    return requirements


INSTALL_REQUIREMENTS = _read_requirements('requirements.txt')

setup(
    name='did_chain',
    packages=find_packages(include=['did_chain']),
    version='0.1.0',
    description='some description',
    author='Geovane Fedrecheski',
    license='MIT',
    install_requires=INSTALL_REQUIREMENTS,
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)
