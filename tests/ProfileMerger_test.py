import unittest
from pprint import pprint

from ProfileMerger import ProfileMerger, PROFILE_A, PROFILE_B, PROFILE_MERGED, Profile, ValueMerge
import models


class ProfileMerger_test(unittest.TestCase):
    def setUp(self):
        self.profile_a = Profile(PROFILE_A, 'tests/test_a.profile')
        self.profile_b = Profile(PROFILE_B, 'tests/test_b.profile')
        self.merger = ProfileMerger(None, None, self.profile_a, self.profile_b)
        
        
    def test_merge(self):
        self.merger.merge_and_save()
        pprint(self.merger.profile_merged.diffs)
        self.assertTrue(self.merger.profile_merged.is_merged)
        self.assertEqual(len(self.merger.profile_merged.diffs), 11)
    
if __name__ == '__main__':
    unittest.main()