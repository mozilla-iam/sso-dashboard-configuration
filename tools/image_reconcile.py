#!/bin/sh
'''which' python >/dev/null 2>&1 && exec python "$0" "$@" || exec python3 "$0" "$@"
'''
# The above noise is, "hey bash, run python or python3, whatever you find".
# Because, there's no good way to do this across OSes until people figure
# it out and pick one executable name to rule them all.
#
# It looks like magic, but it's COOL.
# * the shebang /bin/sh says "run this script as shell."
# sh says '', that's an empty string, okay. and 'which' is just wrapping around`which`.
# sh then does the `which` command that looks for `python`.
# If found, exec python using this script (as $0 and passing along any args)
#    This is what you're "supposed" to use.  OSX has this.
# If not found, exec python3
#    This is the less-prefered path but what Linux has.
# At this point we've exec'ed out of sh, so the rest of the body doesn't matter.
# But now, going back through this as python, 3 single quotes?  That block is
# a string literal comment, and python skips right over it.
# Ta-da, a python-interpreter-name-agnostic python3 script, assisted by bash.
#
#
#
#   This script finds discrepancies between what logos are declared in apps.yml
#   and what files exist in the images folder, then tells you what to clean up.
#
import os
import sys
import subprocess
import yaml
# ^^ pip install PyYAML

# paths relative to the repo root
APPS_YAML_FILE = 'apps.yml'
IMAGES_DIRECTORY = 'images'


def get_images_from_directory(images_directory):
    '''
        Input: str filepath to the images directory
        Output: set(str) of filenames in the images directory
    '''
    image_listing = os.listdir(images_directory)
    image_set = set(image_listing)
    return image_set


def get_images_from_yaml(yaml_filename):
    '''
        Input: str filepath to apps.yml
        Output: set(str) of filenames refered to in 'logo' attributes
    '''
    image_set = set()
    with open(yaml_filename, 'r') as yaml_fh:
        conf = yaml.safe_load(yaml_fh)
        yaml_fh.close()
    apps = conf['apps']
    for app_entry in apps:
        # Each entry has a key of the literal 'application' and then a dict of values...
        app_data = app_entry['application']
        # ... and that defines a logo.  That currently always exists but might not.
        logo = app_data.get('logo')
        if logo:
            image_set.add(logo)
    return image_set


def main():
    ''' main function '''

    if sys.version_info >= (3, 7):
        # 3.7 is when run() got new stdout handling.
        root_finding_process = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                                              capture_output=True,
                                              check=True)
    elif sys.version_info >= (3, 5):
        # 3.5 is when run() came in
        root_finding_process = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                                              stdout=subprocess.PIPE,
                                              check=True)
    else:
        print('Unable to execute subprocess.  Development effort goes here.')
        sys.exit(2)

    github_root = root_finding_process.stdout.decode('utf-8').strip()

    apps_yaml_file = os.path.join(github_root, APPS_YAML_FILE)
    images_directory = os.path.join(github_root, IMAGES_DIRECTORY)

    yaml_image_set = get_images_from_yaml(apps_yaml_file)
    directory_image_set = get_images_from_directory(images_directory)

    yaml_but_no_image = yaml_image_set - directory_image_set
    image_but_no_yaml = directory_image_set - yaml_image_set

    if yaml_but_no_image:
        print(f'Logo names in {APPS_YAML_FILE}, with no image found in {IMAGES_DIRECTORY}')
        print('  (This is important to fix.)')
        print('-----')
        for item in sorted(yaml_but_no_image):
            print(item)
        print('')

    if image_but_no_yaml:
        print(f'Logo files in {IMAGES_DIRECTORY} that are not referenced in {APPS_YAML_FILE}')
        print('  (This is debris, cleanup would be nice.)')
        print('-----')
        for item in sorted(image_but_no_yaml):
            print(item)
        print('')

if __name__ == '__main__':
    main()
