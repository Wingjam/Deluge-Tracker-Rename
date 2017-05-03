import os
import sys
import platform
import shutil
import pickle
import argparse

parser = argparse.ArgumentParser(description="Find and replace tracker urls in a Deluge torrents.state")
parser.add_argument("orig_tracker_url", help="The original tracker url to be replaced.", type=str)
parser.add_argument("new_tracker_url", help="The new tracker url to replace the original one.", type=str)
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
print("Replace '{}' with '{}'" .format(args.orig_tracker_url, args.new_tracker_url))
state_file = open(state_file_path, 'rb')
state = pickle.load(state_file)
state_file.close()

state_modified_count = 0
for torrent in state.torrents:
    for tracker in torrent.trackers:
        if tracker['url'] == args.orig_tracker_url:
            tracker['url'] = args.new_tracker_url
            state_modified_count += 1


if state_modified_count:
    shutil.copyfile(state_file_path, state_file_path + '.old')
    state_file = open(state_file_path, 'wb')
    pickle.dump(state, state_file)
    state_file.close()
    print("State Updated ({}/{})".format(state_modified_count, len(state.torrents)))
else:
    print("Nothing to do")
