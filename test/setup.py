from setuptools import find_packages, setup
setup(
    name='fireup',
    packages=find_packages(include=['fireup']),
    version='1.0.0',
    description='Project that contains automated tenancy review following OCI best practices framework',
    author='dralquinta@gmail.com',
    license='UPL',
    install_requires=['oci'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='test_suite',
)