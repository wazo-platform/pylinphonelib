"""
pylinphonelib
-------------

pylinphonelib is a library to drive a linphonec instance from python
"""

from setuptools import find_packages, setup

setup(
    name='pylinphonelib',
    version='0.0',
    license='GPLv3',
    author='Wazo Authors',
    author_email='dev.wazo@gmail.com',
    description='A library to drive linphonec',
    long_description=__doc__,
    packages=find_packages(),
    platforms='any',
)
