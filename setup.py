"""
pylinphonelib
-------------

pylinphonelib is a library to drive a linphonec instance from python
"""

from setuptools import setup

setup(
    name='pylinphonelib',
    version='0.0',
    license='MIT',
    author='Pascal Cadotte Michaud',
    author_email='pascal.cadotte@gmail.com',
    description='A library to drive linphonec',
    long_description=__doc__,
    packages=['linphonelib'],
    platforms='any',
)
