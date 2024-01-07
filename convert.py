import os
import pathlib
import json

folder_path = pathlib.Path('./get_data/games/')
batch_data = []

files = []
for root, dirs, filenames in os.walk(folder_path):
    for filename in filenames:
        files.append(os.path.join(root, filename))

files = [file for file in files if 'model' not in file]
files = [file for file in files if 'batch' not in file]

for file in files:
    id = file.replace('get_data\\games\\', '')[:-4]

    with open(file, 'r') as f:
        text = f.readlines()

    line = text[115].replace('@start "" "League of Legends.exe" "spectator ', '')
    args = line.split(' ')

    batch_data.append({'id': id, 'arg1': args[0], 'arg2': args[1], 'arg3': args[2], 'arg4': args[3].replace('-%RANDOM%%RANDOM%"', '')})

    os.remove(file)

print(len(batch_data))