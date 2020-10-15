from maintcal.tests.lib import MaintcalBrowserTest

class TestChangeDefaultZone(MaintcalBrowserTest):

    #def local_setup(self):
    #    #MaintcalUnitTest.local_setup(self)
    #    pass

    def test_login(self):
        self.dh.insertAvailableDefault(1, 0, 0*60, 24*60 - 1, 24)
        self.dh.insertAvailableDefault(1, 1, 0*60, 24*60 - 1, 24)
        self.dh.insertAvailableDefault(1, 2, 0*60, 24*60 - 1, 24)
        self.dh.insertAvailableDefault(1, 3, 0*60, 24*60 - 1, 24)
        self.dh.insertAvailableDefault(1, 4, 0*60, 24*60 - 1, 24)
        self.dh.insertAvailableDefault(1, 5, 0*60, 24*60 - 1, 24)
        self.dh.insertAvailableDefault(1, 6, 0*60, 24*60 - 1, 24)
        
        import time

        #sel.type("q", "hello world")
        #sel.click("btnG")

        #self.s.open("http://devhost.core:5000/maintcal/admin_console")
        self.s.open("http://devhost.core")
        self.s.wait_for_page_to_load(5000)


        # core_userid
        self.s.type('name=core_userid', 'ed.leafe')

        # core_password

        self.s.type('name=core_password', 'qwerty')

        self.s.click("xpath=/html[@id='mainbody']/body/form/div/table/tbody/tr[5]/td[2]/input[2]")

        time.sleep(5)

        # click on the 2nd button
        #self.s.get_eval("global_view.west.items.items[1].fireEvent('click',global_view.west.items.items[1]);")

        #self.assert_contains('24 hrs')
        #self.assert_contains('48 hrs')
        #time.sleep(3)

