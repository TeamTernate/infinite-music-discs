![GitHub release (latest by date)](https://img.shields.io/github/downloads/TeamTernate/infinite-music-discs/latest/total?label=downloads%20%28latest%29) ![GitHub all releases](https://img.shields.io/github/downloads/TeamTernate/infinite-music-discs/total?label=total%20downloads)

# Infinite Music Discs
A graphical app for adding lots of custom music discs to Minecraft. Creates a resourcepack to add new music tracks and disc textures, and a datapack with custom logic to play the new music discs.

Written in Python with a PyQt5 frontend; compiled into runnable binaries with pyinstaller.

### Supported Systems
64-bit Windows

### How to Install
Download `imd-gui.zip` from the latest release, under Assets. Extract the .zip to a work folder and run the executable inside. Follow the video instructions at [https://www.youtube.com/watch?v=zDXSKYvJXmg](https://www.youtube.com/watch?v=zDXSKYvJXmg) to generate a datapack/resourcepack pair; the datapack and resourcepack will be created in the same folder as the executable.

An example disc texture and a pack.png are provided alongside the executable binary, for convenience.

### Building from Source
The build environment is set up for Windows, though pyinstaller is cross-platform so you could build on macOS or Linux, if you wanted. You would not be able to use the provided build script on any OS other than Windows.
1. Clone this repository.
2. Install Python 3, 64 bit.
3. Add Python to your PATH environment variable.
4. Open a command prompt in the *infinite-music-discs* directory and run `pip install -r requirements.rc`.
5. Try running `main.pyw` to verify the application works in your environment. Make sure you can generate a pack, convert files to .ogg with pyffmpeg, etc.
6. Run `build.bat` to compile the source into a Windows executable binary.
7. Run your executable! Note that your antivirus may flag your executable as suspicious because it's an unknown, unsigned program. You should be safe to ignore this warning, but of course, always use caution and common sense when ignoring the warnings of your antivirus.
