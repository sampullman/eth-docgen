from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='eth-docgen',
    version='0.1.0',
    description='Generate html documentation from Ethereum smart contracts',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/sampullman/eth-docgen/',

    classifiers=[
    ],

    keywords='ethereum documentation',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['yattag>=1.10.0'],

    entry_points={
        'console_scripts': [
            'eth-docgen=docgen:main',
        ],
    },

    project_urls={
        'Bug Reports': 'https://github.com/sampullman/eth-docgen/issues',
        'Source': 'https://github.com/sampullman/eth-docgen/',
    },
)