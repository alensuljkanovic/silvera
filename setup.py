#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import codecs
from setuptools import setup


VERSIONFILE = "silvera/__init__.py"
VERSION = None
for line in open(VERSIONFILE, "r").readlines():
    if line.startswith('__version__'):
        VERSION = line.split('"')[1]

if not VERSION:
    raise RuntimeError('No version defined in silvera.__init__.py')

README = codecs.open(os.path.join(os.path.dirname(__file__), 'README.md'),
                     'r', encoding='utf-8').read()

setup(
    name='silvera',
    version=VERSION,
    description='Tool for generating microservice architectures.',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Alen Suljkanovic',
    author_email='alienized91@gmail.com',
    license='MIT',
    packages=["silvera", "silvera.export", "silvera.generator",
              "silvera.lang"],
    include_package_data=True,
    install_requires=["textx", "jinja2", "click"],
    tests_require=[
        'pytest',
        'openapi_spec_validator'
    ],
    keywords="microservices dsl generator compiler",
    url="https://github.com/alensuljkanovic/silvera",
    entry_points={
        'console_scripts': [
            'silvera = silvera.cli:silvera'
        ],

        'silvera_commands': [
            'check = silvera.cli.check',
            'compile = silvera.cli.compile',
            'list_generators = silvera.cli.list_generators',
            'list_evaluators = silvera.cli.list_evaluators'
        ],

        'silvera_generators': [
            # Java generator is built-in
            'java = silvera.generator.java_generator:java',
        ],

        'silvera_evaluators': [
            # Built-in evaluator
            'default_evaluator = silvera.evaluation.builtin:default_evaluator',
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Interpreters',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ]

)
