"""
Hello World app for running Python apps on Bluemix
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='march-madness',
    version='1.0.0',
    description='Chatbot asking and answering questions relating to NCAA 2018 final teams',
    long_description='Chatbot asking and answering questions relating to NCAA 2018 final teams',
    url='https://github.com/VietHTranTraining/villanova-michigan-chatbot',
    license='Apache-2.0'
)
