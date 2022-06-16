#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.md') as history_file:
    history = history_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read()

test_requirements = [ ]

setup(
    author="Data Science",
    author_email='trinker@anthology.com',
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    description="Collection of utilities to for the Data Science team",
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='ds',
    name='ds',
    packages=find_packages(include=['ds', 'ds.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://dev.azure.com/campuslabs/Data%20Science/_git/ds-python-packages',
    version='0.1.12',
    zip_safe=False,
)
