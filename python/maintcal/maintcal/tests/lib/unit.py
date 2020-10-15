"""
Superclass for maintcal unit tests.

Unit tests are for anything that is independent of 
the maintcal controllers.

These tests should not require the paster framework.

"""
from maintcal_test import MaintcalTest
from mocker import ANY, KWARGS, ARGS

class MaintcalUnitTest(MaintcalTest):
    pass
