"""
pylinphonelib
-------------

pylinphonelib is a library to drive a linphonec instance from python
"""

from setuptools import setup

setup(
    name='pylinphonelib',
    version='0.0',
    license='GPLv3',
    author='Avencall',
    author_email='xivo-dev@lists.proformatique.com',
    description='A library to drive linphonec',
    long_description=__doc__,
    packages=['linphonelib'],
    platforms='any',
)
