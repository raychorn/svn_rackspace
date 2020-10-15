"""
Superclass for maintcal functional tests.
"""
from maintcal_test import MaintcalTest
import pkg_resources
import paste.fixture
import paste.script.appinstall
from paste.deploy import loadapp
import os
import sys
from mocker import ANY, KWARGS, ARGS

class MaintcalFunctionalTest(MaintcalTest):
    pass
