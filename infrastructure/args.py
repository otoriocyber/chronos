import argparse
import os


class Args:
    def __init__(self):
        self.parser = self._create_parser()

    @staticmethod
    def _create_parser():
        # Get the args
        parser = argparse.ArgumentParser()
        # Each event will have different index for better incident management
        parser.add_argument('-n', "--eventname", type=str, help='The name of the current event', required=True)
        # The evidences path is the root of the folder with the host name with an internal structure similar to the windows
        # structure - i.e DESKTOP-1234567\C, Laptop01\C
        parser.add_argument('-e', "--evidences", type=str, help='Path of the evidences to parse', required=True)
        # The DB details
        parser.add_argument("--host", type=str, help='The db address')
        parser.add_argument('-p', "--port", type=str, help='The db port', default=9200)
        parser.add_argument('--db-user', type=str, help='The db user', default=None)
        parser.add_argument('--db-password', type=str, help='The db password', default=None)
        # Uploading to DB using bulk, you may want to change the value for optimize the performance of your facilities
        parser.add_argument("--bulk", type=str, help='The bulk size to index with', default=500)
        # Add paths from file
        parser.add_argument("--file", type=str, help='Json with paths to parse (add to defaults)')
        # Use only paths from file
        parser.add_argument("--file-only", type=str, help='Json with paths to parse (ignore defaults)')
        # Keep the temp folder with the parsed results
        parser.add_argument("--dump", help="Dump the results to folder")
        return parser

    def validate(self):
        args = self.parser.parse_args()
        evidences_path = args.evidences
        if not os.path.exists(evidences_path):
            print("[!] The path supplied doesn't exist")
            self.parser.print_help()
            exit(1)
