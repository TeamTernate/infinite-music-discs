#!/usr/bin/env python3

import os
import subprocess
import shutil
import platform
from pathlib import Path
from zipfile import ZipFile
import tarfile
import hashlib

import version



# read in version number
# detect os
# copy example files
# copy binary
# generate version identifier file
# sign exe (windows)
# zip files (windows)
# tar files (linux)
# calculate md5sum of bin and write to a file



# Script parameters
system = platform.system()
version_literal = f'v{version.MAJOR}.{version.MINOR}.{version.PATCH}'

release_dir = Path(os.path.dirname(__file__)) / '..' / 'release'
bin_dir = Path(os.path.dirname(__file__)) / '..' / 'bin'
ref_dir = release_dir / 'reference'
out_dir = release_dir / version_literal

if system == 'Windows' :
    bin_name = 'imd-gui.exe'
    version_file_name = f'{version_literal}-win64.txt'
    zip_file_name = 'imd-gui-win64.zip'
    md5_file = 'md5_win.txt'
else:
    bin_name = 'imd-gui'
    version_file_name = f'{version_literal}-ubuntu-22.04'
    zip_file_name = 'imd-gui-linux64.tar.gz'
    md5_file = 'md5_linux.txt'

# Begin script
shutil.rmtree(out_dir, ignore_errors=True)
os.mkdir(out_dir)

shutil.copy(ref_dir / 'example-disc.png', out_dir)
shutil.copy(ref_dir / 'pack.png', out_dir)
shutil.copy(ref_dir / 'README.txt', out_dir)

with open(out_dir / version_file_name, 'w') as f:
    pass

shutil.copy(bin_dir / bin_name, out_dir)

if system == 'Windows':
    password = input("Enter code signing password: ")
    subprocess.run([
        'signtool', 'sign',
        '/f', f'{out_dir}\..\Sectigo Code Signing Certificate Exp 8-30-2025.pfx',
        '/p', f'{password}',
        '/tr', 'http://timestamp.sectigo.com',
        '/td', 'SHA256', '/fd', 'sha256',
        f'{out_dir}\imd-gui.exe'
    ], check=True)

    subprocess.run([
        'signtool', 'verify',
         '/pa', '/v', f'{out_dir}\imd-gui.exe'
    ], check=True)

    with ZipFile(out_dir / zip_file_name, 'w') as zip:
        zip_files = ['example-disc.png', 'pack.png', bin_name, version_file_name]
        [zip.write(out_dir / f, Path('.') / f) for f in zip_files]

else:
    with tarfile.open(out_dir / zip_file_name, 'w') as zip:
        zip_files = ['example-disc.png', 'pack.png', bin_name, version_file_name]
        [zip.add(out_dir / f, Path('.') / f) for f in zip_files]

with open(out_dir / md5_file, 'w') as f:
    f.write(hashlib.md5(open(out_dir / bin_name, 'rb').read()).hexdigest())
