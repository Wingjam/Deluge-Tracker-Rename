import os
import sys
import platform
import shutil
import pickle
import argparse
import re
from sets import Set
import time

parser = argparse.ArgumentParser(description="Find and replace tracker urls in a Deluge torrents.state")
parser.add_argument(
    "orig_tracker",
    help="The original tracker regular expression url (with n possible groups) to be replaced."
         " i.e. https://tracker.t411.ai/(\w+)/announce",
    type=str
)
parser.add_argument(
    "new_tracker",
    help="The new tracker url to replace the original one with \\n where n is the group number from orig_tracker."
         " i.e. http://tracker.t411.al/\\1/announce",
    type=str
)
args = parser.parse_args()

if platform.system() in ('Windows', 'Microsoft'):
    state_file_path = os.path.join(os.environ.get('APPDATA'), 'deluge', 'state', 'torrents.state')
    deluge_dir = os.path.join(os.environ['ProgramFiles'], 'Deluge')
    if os.path.isdir(deluge_dir):
        sys.path.append(deluge_dir)
        for item in os.listdir(deluge_dir):
            if item.endswith(('.egg', '.zip')):
                sys.path.append(os.path.join(deluge_dir, item))
else:
    state_file_path = os.path.expanduser('~/.config/deluge/state/torrents.state')

print("State file : {}".format(state_file_path))
print("Replace '{}' with '{}'".format(args.orig_tracker, args.new_tracker))
state_file = open(state_file_path, 'rb')
state = pickle.load(state_file)
state_file.close()

state_updated = Set()
state_not_updated = Set()

for torrent in state.torrents:
    for tracker in torrent.trackers:
        new_string, number_of_subs_made = re.subn(args.orig_tracker, args.new_tracker, tracker['url'])
        if number_of_subs_made:
            tracker['url'] = new_string
            state_updated.add(new_string)
        else:
            state_not_updated.add(new_string)

if state_updated:
    shutil.copyfile(state_file_path, "{}.{}.old".format(state_file_path, time.time()))
    state_file = open(state_file_path, 'wb')
    pickle.dump(state, state_file)
    state_file.close()

    print("\nState Updated : {}".format(len(state_updated)))
    for state in state_updated:
        print(state)

    print("\nState NOT Updated : {}".format(len(state_not_updated)))
    for state in state_not_updated:
        print(state)
else:
    print("Nothing to do ...")
    print("\nState NOT Updated : {}".format(len(state_not_updated)))
    for state in state_not_updated:
        print(state)
