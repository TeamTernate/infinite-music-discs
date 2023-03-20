import os
import subprocess

import version

build_dir = os.path.dirname(__file__)
version_csv = f'{version.MAJOR}, {version.MINOR}, 0, 0'
version_literal = f'{version.MAJOR}.{version.MINOR}.0.0'

# Write a copy of 'version.rc' with the version numbers autopopulated from version.py
with open(os.path.join(build_dir, 'version.rc'), 'r') as v_orig:
    with open(os.path.join(build_dir, 'version.rc.tmp'), 'w') as v_temp:
        for line in v_orig.readlines():
            v_temp.write(line.format(version_csv=version_csv, version_literal=version_literal))

# Run pyinstaller
# Raise exception if pyinstaller errors out; calling process can check STDERR to detect pass/fail
pyinstaller_cmd = [
    'pyinstaller', 'main.pyw',
    '--onefile',
    '--clean',
    '--noconfirm',
    '--version-file', 'build/version.rc.tmp',
    '--add-data', f'data/*{os.pathsep}data',
    '--name', 'imd-gui',
    '--icon', 'data/jukebox_256.ico',
    '--distpath', 'bin',
    '--workpath', 'build'
]

subprocess.run(pyinstaller_cmd, check=True)
