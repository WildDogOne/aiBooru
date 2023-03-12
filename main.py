import argparse
from content.functions import upload_directory

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='aiBooru',
                                     description='A CLI Interface for Danbooru Style image boards')
    parser.add_argument("-d",
                        "--directory",
                        help="Directory containing files you want to upload",
                        type=str,
                        required=False)
    args = parser.parse_args()
    if args.directory:
        upload_directory(args.directory)
    else:
        parser.print_help()
