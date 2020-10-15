from maintcal.tests.lib import MaintcalUnitTest

from datetime import timedelta

from maintcal.lib import normalize
from maintcal.lib.date import timedelta2hours, timedelta_to_total_seconds

class TestNormalize(MaintcalUnitTest):
    
    def test_normalize_boolean(self):
        self.assert_(normalize.normalize_boolean('true'))
        self.assert_(normalize.normalize_boolean('TRUE'))
        self.assert_(not normalize.normalize_boolean('false'))
        self.assert_(not normalize.normalize_boolean('FALSE'))
        self.assert_(normalize.normalize_boolean(u'true'))
        self.assert_(normalize.normalize_boolean('1'))
        self.assert_(not normalize.normalize_boolean('0'))
    
    def test_normalize_interval(self):
        self.assertRaises(ValueError, normalize.normalize_interval,'true')
        self.assertRaises(ValueError, normalize.normalize_interval, True)
        self.assertEqual(normalize.normalize_interval('0.5'), timedelta(minutes=30))
        self.assertEqual(normalize.normalize_interval(u'0.25'), timedelta(minutes=15))
        self.assertEqual(normalize.normalize_interval('3.25'), timedelta(minutes=195))
        self.assertEqual(normalize.normalize_interval('0'), timedelta(minutes=0))

    def test_timedelta_to_total_seconds(self):
        self.assertEqual(timedelta_to_total_seconds(timedelta(seconds=5)), 5)
        self.assertEqual(timedelta_to_total_seconds(timedelta(minutes=1, seconds=5)), 65)
        self.assertEqual(timedelta_to_total_seconds(timedelta(hours=1, seconds=5)), 3605)
        self.assertEqual(timedelta_to_total_seconds(timedelta(days=1, seconds=5)), 86405)
        self.assertEqual(timedelta_to_total_seconds(timedelta(seconds=-5)), -5)
        self.assertEqual(timedelta_to_total_seconds(timedelta(days=-1, seconds=64800)), -21600)
    
    def test_timedelta2hours(self):
        self.assertEqual(timedelta2hours(timedelta(seconds=3600)), 1)
        self.assertEqual(timedelta2hours(timedelta(days=1)), 24)
        self.assertEqual(timedelta2hours(timedelta(seconds=5400)), 1.5)
        self.assertEqual(timedelta2hours(timedelta(days=-1, seconds=64800)), -6)
        self.assertEqual(timedelta2hours(timedelta(days=-1, seconds=66600)), -5.5)
