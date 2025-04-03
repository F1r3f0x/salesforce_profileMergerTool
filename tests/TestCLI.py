import unittest

import cli


class TestCLI(unittest.TestCase):
    def test_cli_merge(self):

        # Test Args
        test_args = ['-a', 'tests/test_a.profile', '-b', 'tests/test_b.profile', '-o', 'tests/test_output.profile', '-l', 'tests/test_log']
        args = cli.parse_args(test_args)

        self.assertEqual(args.profile_a, 'tests/test_a.profile')
        self.assertEqual(args.profile_b, 'tests/test_b.profile')
        self.assertEqual(args.output, 'tests/test_output.profile')
        self.assertEqual(args.log, 'tests/test_log')
        
        # Run merge
        cli.main(test_args)

if __name__ == '__main__':
    unittest.main()