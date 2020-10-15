from maintcal.tests.lib import url_for, MaintcalFunctionalTest

class TestAccountsController(MaintcalFunctionalTest):

    def test_index(self):
        response = self.app.get(url_for(controller='accounts'))
        # Test response...
