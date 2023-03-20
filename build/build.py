import os
import subprocess
import src.version as version

build_dir = os.path.dirname(__file__)

version_csv = f'{version.MAJOR}, {version.MINOR}, 0, 0'
version_literal = f'{version.MAJOR}.{version.MINOR}.0.0'

# Write a copy of 'version.rc' with the version numbers autopopulated from version.py
with open(os.path.join(build_dir, 'version.rc'), 'r') as v_orig:
    with open(os.path.join(build_dir, 'version.rc.tmp'), 'w') as v_temp:
        for line in v_orig.readlines():
            v_temp.write(line.format(version_csv=version_csv, version_literal=version_literal))
