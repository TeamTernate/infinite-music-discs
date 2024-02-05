#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#Infinite Music Discs cross-platform build script
#Script by link2_thepast

import os
import subprocess
import argparse

import version

# Script parameters
build_dir = os.path.dirname(__file__)

# Version information to be embedded inside executable (Windows only)
version_csv = f'{version.MAJOR}, {version.MINOR}, {version.PATCH}, 0'
version_literal = f'{version.MAJOR}.{version.MINOR}.{version.PATCH}.0'
company_name = "Team Ternate"
product_name = "Infinite Music Discs Generator"
file_description = "Add lots of custom music discs to Minecraft"
copyright = f"Copyright (c) {company_name}"

# Use argparse to decide whether to run nuitka or pyinstaller
# nuitka is only used on Windows at this time due to incompatibility with the Linux build environment
parser = argparse.ArgumentParser(prog=f"{product_name} Build Script",
                                 description=f"Builds {product_name} for Windows or Linux")

parser.add_argument('-n', '--nuitka', action='store_true', help='Use nuitka to compile instead of pyinstaller')
args = parser.parse_args()

# Write a copy of 'version.rc' with the version numbers autopopulated from version.py
# Use **locals() to grab all currently-defined local variables and format the
#   template 'version.rc' with them (grabs all locals as a dict and splats them with
#   the ** operator into a flattened list)
with open(os.path.join(build_dir, 'version.rc'), 'r') as v_orig:
    with open(os.path.join(build_dir, 'version.rc.tmp'), 'w') as v_temp:
        for line in v_orig.readlines():
            v_temp.write(line.format(**locals()))

# Command to run pyinstaller
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

# Command to run nuitka
nuitka_cmd = [
    'python', '-m', 'nuitka', 'main.pyw',
    '-o', 'imd-gui.exe',
    '--onefile',
    '--plugin-enable=pyside6',
    '--disable-console',
    '--include-data-dir=data=data',
    '--windows-icon-from-ico=data/jukebox_256.ico',
    f'--company-name={company_name}',
    f'--product-name={product_name}',
    f'--file-version={version_literal}',
    f'--product-version={version_literal}',
    f'--file-description={file_description}',
    f'--copyright={copyright}'
]

# Build with selected program
# Raise exception if the build program errors out; calling process can check STDERR to detect pass/fail
if(args.nuitka):
    subprocess.run(nuitka_cmd, check=True)
else:
    subprocess.run(pyinstaller_cmd, check=True)
