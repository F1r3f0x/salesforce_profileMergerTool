import unittest

from ProfileMerger import ProfileMerger, PROFILE_A, PROFILE_B, PROFILE_MERGED, Profile, ValueMerge


class TestProfileMerger(unittest.TestCase):
    def setUp(self):
        self.profile_a = Profile(PROFILE_A, 'tests/test_a.profile')
        self.profile_b = Profile(PROFILE_B, 'tests/test_b.profile')
        self.output = Profile(PROFILE_MERGED, 'tests/test_output.profile')
        self.merger = ProfileMerger(None, None, None, self.profile_a, self.profile_b, self.output)


    def test_ab_merge(self):
        self.merger.merge_and_save()
        self.assertTrue(self.merger.profile_merged.is_merged)
        self.assertEqual(len(self.merger.profile_merged.diffs), 20)


if __name__ == '__main__':
    unittest.main()