#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read()

test_requirements = ['pytest>=3', ]

setup(
    author="Anthology Data Science",
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
    description="A collection of tools for Anthology iX",
    install_requires=requirements,
    long_description=readme,
    include_package_data=True,
    keywords='sneetches',
    name='sneetches',
    packages=find_packages(include=['sneetches', 'sneetches.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://dev.azure.com/campuslabs/Data%20Science/_git/sneetches',
    version='0.1.2',
    zip_safe=False,
)
