![GitHub release (latest by date)](https://img.shields.io/github/downloads/TeamTernate/infinite-music-discs/latest/total?label=downloads%20%28latest%29) ![GitHub all releases](https://img.shields.io/github/downloads/TeamTernate/infinite-music-discs/total?label=total%20downloads) ![Static Badge](https://img.shields.io/badge/available_for-1.14_%E2%80%94_1.21-blue)

# Infinite Music Discs
A desktop app for adding lots of custom music discs to Minecraft. Use the app to create a resourcepack that adds new music tracks and disc textures, and a datapack with custom logic to play the new music discs. An example disc texture and a pack.png are provided alongside the app to get you started.

Written in Python with a PyQt6 frontend; compiled into runnable binaries with nuitka (Windows) and pyinstaller (Linux).

## Runs On
- 64-bit Windows
- 64-bit Linux
- Any computer with Python 3.11 installed

## How to Install

### Windows:
1. Download `imd-gui-win64.zip` from the latest release, under Assets.
2. Extract the .zip to a work folder and run the executable inside.
3. Follow the video instructions at [https://www.youtube.com/watch?v=zDXSKYvJXmg](https://www.youtube.com/watch?v=zDXSKYvJXmg) to generate a datapack/resourcepack pair. The datapack and resourcepack will be created in the same folder as the executable.

### Linux:
1. Download `imd-gui-linux64.tar.gz` from the latest release, under Assets.
2. Extract the tarball to a work folder, make `imd-gui` executable, and run it:
```bash
$ tar -xvf imd-gui-linux64.tar.gz
$ chmod +x imd-gui
$ ./imd-gui
```
3. Follow the video instructions linked above to generate a datapack/resourcepack pair. The datapack and resourcepack will be created in the same directory as the executable.

### Other:
1. Install `git` and clone this repository.
2. Install Python 3.11, 64 bit.
3. Add Python to your PATH environment variable (if necessary).
4. Open a terminal in the `infinite-music-discs` directory and run `pip install -r requirements.rc`.
5. Launch the app by running `main.pyw` and follow the video instructions linked above to generate a datapack/resourcepack pair. The datapack and resourcepack will be created in the same directory as `main.pyw`.

## Building from Source
The build environment is set up for Windows and Linux, though pyinstaller is cross-platform so you could build on macOS too.

### Windows:
1. Install `git` and clone this repository.
2. Install Python 3.11, 64 bit.
3. Add Python to your PATH environment variable (if necessary).
4. Open a command prompt in the `infinite-music-discs` directory and run `pip install -r requirements.rc`.
5. Try running `main.pyw` to verify the application works in your environment. Make sure you can generate a pack, convert files to .ogg with pyffmpeg, etc.
6. Run `build_win_nuitka.bat` to compile the source into a Windows executable binary. The output exe will be placed in `infinite-music-discs/bin`.
7. Run your executable! Note that your antivirus may flag your executable as suspicious because it's an unknown, unsigned program. You should be safe to ignore this warning, but of course, always use caution and common sense when ignoring the warnings of your antivirus.

### Linux:
1. Clone this repository:
```bash
$ git clone https://github.com/TeamTernate/infinite-music-discs
```
2. Run the build script. If dependencies like python3 are not installed, it may ask for sudo privileges to install them:
```bash
$ cd infinite-music-discs
$ ./build_linux.sh
```
3. The built binary will be placed in `infinite-music-discs/bin`. You may need to make it executable before it can be run:
```bash
$ chmod +x bin/imd-gui
$ ./bin/imd-gui
```

#### Supported Build Linux distributions:
Debian-based:
- Debian
- Ubuntu (all flavors)
- Elementary OS
- Sparky Linux

Others:
- Fedora (and spins)
- Arch Linux (and all Arch-based distros, such as Manjaro)

#### Notes for Linux users:
- If your distribution ships Python 3 by default (under the name python3), then you don't need to do anything prior to running the script.
- The script will auto-install all the required dependencies. You might need to provide your sudo password.
- A tmp directory will be created (inside the cloned repository) where temporary files will be stored.
