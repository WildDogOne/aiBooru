import argparse
from content.functions import upload_directory

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='aiBooru',
                                     description='A CLI Interface for Danbooru Style image boards')
    parser.add_argument("-d",
                        "--directory",
                        help="Directory containing files you want to upload."
                             "Each file needs a yaml as a descriptor, they will be automatically created."
                             "By default images are only uploaded once, state is stored in data/*.json"
                             "Add -f if you want to force upload everything again",
                        type=str,
                        required=False)
    parser.add_argument("-f",
                        "--force",
                        help="Force upload of all images, ignore state stored in data/*.json",
                        action='store_true',
                        required=False)
    args = parser.parse_args()
    if args.directory:
        upload_directory(args.directory, args.force)
    else:
        parser.print_help()
