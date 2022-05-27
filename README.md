![GitHub release (latest by date)](https://img.shields.io/github/downloads/TeamTernate/infinite-music-discs/latest/total?label=downloads%20%28latest%29) ![GitHub all releases](https://img.shields.io/github/downloads/TeamTernate/infinite-music-discs/total?label=total%20downloads)

# Infinite Music Discs
A graphical app for adding lots of custom music discs to Minecraft. Creates a resourcepack to add new music tracks and disc textures, and a datapack with custom logic to play the new music discs.

Written in Python with a PyQt5 frontend; compiled into runnable binaries with pyinstaller.

### Supported Operating Systems
- 64-bit Windows
- 64-bit Linux

### How to Install
- Windows Installation:

Download `imd-gui.zip` from the latest release, under Assets. Extract the .zip to a work folder and run the executable inside. Follow the video instructions at [https://www.youtube.com/watch?v=zDXSKYvJXmg](https://www.youtube.com/watch?v=zDXSKYvJXmg) to generate a datapack/resourcepack pair; the datapack and resourcepack will be created in the same folder as the executable.

- Linux Installation:

Download `imd-gui` from the latest release. Then, make the file executable and run it:
```bash
$ chmod +x imd-gui
$ ./imd-gui
```

An example disc texture and a pack.png are provided alongside the executable binary, for convenience.

### Building from Source
The build environment is set up for Windows and Linux, though pyinstaller is cross-platform so you could build on macOS too.

#### On Windows:
1. Clone this repository.
2. Install Python 3, 64 bit.
3. Add Python to your PATH environment variable.
4. Open a command prompt in the *infinite-music-discs* directory and run `pip install -r requirements.rc`.
5. Try running `main.pyw` to verify the application works in your environment. Make sure you can generate a pack, convert files to .ogg with pyffmpeg, etc.
6. Run `build.bat` to compile the source into a Windows executable binary.
7. Run your executable! Note that your antivirus may flag your executable as suspicious because it's an unknown, unsigned program. You should be safe to ignore this warning, but of course, always use caution and common sense when ignoring the warnings of your antivirus.

#### On Linux:
Clone this repository:
```bash
$ git clone https://github.com/TeamTernate/infinite-music-discs
```
Run the build script:
```bash
$ cd infinite-music-discs
$ ./build.sh
```

#### Supported Linux distributions (applies only to the bash script):
Debian-based:
- Debian
- Ubuntu (all flavors)
- Elementary OS
- Sparky Linux

Others:
- Fedora (and spins)
- Arch Linux (and all Arch-based distros, such as Manjaro)

#### Notes for Linux users:
- If your distribution ships Python 3 by default, then you don't need to do anything prior to running the script.
- The script will auto-install all the required dependencies. You might need to provide your sudo password.
- A tmp directory will be created (inside the cloned repository) where logs and other temporary files will be stored.
