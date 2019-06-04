pylinphonelib
=============
[![Build Status](https://jenkins.wazo.community/buildStatus/icon?job=pylinphonelib)](https://jenkins.wazo.community/job/pylinphonelib)

pylinphonelib is a python library to drive the linphonec application from python.


Requirements
------------

* linphonec


Docker
------

## Since PJSIP, the docker doesn't work for acceptance tests

It is possible to use the wazopbx/wazo-linphone docker image to run linphonec. To enable this
feature, set the USE_DOCKER environment variable.
