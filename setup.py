#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=7.0',
    'pandas',
    'kikit',
    'pcbnewTransition'
]

test_requirements = [ ]

setup(
    author="Simon Hobbs",
    author_email='simon.hobbs@electrooptical.net',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Python Boilerplate contains all the boilerplate you need to create a Python package.",
    entry_points={
        'console_scripts': [
            'kikit_multipanel=kikit_multipanel.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='kikit_multipanel',
    name='kikit_multipanel',
    packages=find_packages(include=['kikit_multipanel', 'kikit_multipanel.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/snhobbs/kikit_multipanel',
    version='0.1.0',
    zip_safe=False,
)
