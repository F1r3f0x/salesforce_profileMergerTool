import argparse
from utils import setup_logging
from ProfileMerger import ProfileMerger

LOGFILE_NAME = 'profilemerger'

def parse_args(args=None):
    """
    Parses command line arguments to create a Profile Merger.

    Returns:
        argparse.Namespace: The parsed arguments.

    Raises:
        SystemExit: If required arguments are missing.
    """
    parser = argparse.ArgumentParser(
        prog='ProfileMerger',
        description='F1r3f0x\'s Salesfoce Profile Merger.'
    )
    parser.add_argument('-a', '--profile_a', required=True, help='Path to Profile A (Base)')
    parser.add_argument('-b', '--profile_b', required=True, help='Path to Profile B (Other)')
    parser.add_argument('-o', '--output', required=True, help='Output file path')
    parser.add_argument('-l', '--log', default=LOGFILE_NAME, help='Log file name')

    return parser.parse_args(args)


def main(args=None):
    args = parse_args(args)
    setup_logging(args.log)

    merger = ProfileMerger(args.profile_a, args.profile_b, args.output)
    merger.merge_and_save()


if __name__ == '__main__':
    main()