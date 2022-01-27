from setuptools import find_packages, setup, os

def _read_requirements(file_name):
    """
    Returns list of required modules for 'install_requires' parameter. Assumes
    requirements file contains only module lines and comments.
    """
    requirements = []
    with open(os.path.join(file_name)) as f:
        for line in f:
            if not line.startswith('#'):
                requirements.append(line)
    return requirements


INSTALL_REQUIREMENTS = _read_requirements('requirements.txt')

setup(
    name='did_chain',
    packages=find_packages(include=['did_chain']),
    version='0.1.0',
    description='some description',
    author='jose da silva',
    license='MIT',
    install_requires=INSTALL_REQUIREMENTS,
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)
