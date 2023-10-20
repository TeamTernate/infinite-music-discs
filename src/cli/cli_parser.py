from argparse import ArgumentParser, Namespace

from src.cli.types import DPRPVerPair, Settings
from src.definitions import PackFormatsDict, DiscListEntryContents, DiscListContents

from src.cli.logger import *
from csv import reader

from pathlib import Path


def is_legacy_version(mc_ver: str) -> bool:
    mc_ver_val: list[int] = [int(i) for i in mc_ver.split(".")]
    return mc_ver_val <= [1, 19, 3]


def get_dp_rp_version(mc_ver: str) -> DPRPVerPair:
    # find the corresponding dp&rp version of the game.
    matching_version = None
    for version, values in PackFormatsDict.items():
        if '-' in version:
            start, end = version.split(' - ')
            if start <= mc_ver <= end:
                matching_version = version
                break
        elif version == mc_ver:
            matching_version = version
            break

    if matching_version:
        info(f"matched game version:{matching_version}")
        dp_rp_versions = PackFormatsDict[matching_version]
        return dp_rp_versions
    else:
        error(f"unknown game version{mc_ver}。")


def absolute_path(input_path: str):
    return str(Path(input_path).absolute())


class CLIParser:
    _parse_result: Namespace

    # Namespace(disc_entries_file='123', minecraft_version='1.2.0', use_concurrent=False, mix_mono=False,
    # package_name='infinite_music_discs', dest_dir='.', compress_output=False)

    def __init__(self):
        parser = ArgumentParser(prog="mc music packer")

        parser.add_argument("-f", "--disc-entries-file", type=str, required=True,
                            help="a csv file delimited by semicolon, "
                                 "each line of which contains texture_file;track_file;title;internal_name.")
        parser.add_argument("-g", "--minecraft-version", type=str, required=True,
                            help="specify a game version, support 1.14 - 1.20.2",
                            default="1.20.2")
        parser.add_argument("-p", "--use-parallel", action='store_true',
                            help="allow convert operations run in parallel")
        parser.add_argument("-m", "--mix-mono", action='store_true',
                            help="mix mono, just like the song is played from the jukebox.")
        parser.add_argument("-n", "--package-name", type=str, default="infinite_music_discs",
                            help="package name")
        parser.add_argument("-o", "--output-dir", type=str, default=".", help="the output directory of rp&dp.")
        parser.add_argument("-z", "--compress-output", action='store_true', help="compress output pack to zip")
        parser.add_argument("-c", "--cover-image", type=str, default='', help="cover image of the pack")

        self._parse_result = parser.parse_args()
        self.disc_entries_file: str = self._parse_result.disc_entries_file
        self.minecraft_version: str = self._parse_result.minecraft_version
        self.use_parallel: bool = self._parse_result.use_parallel
        self.mix_mono: bool = self._parse_result.mix_mono
        self.package_name: str = self._parse_result.package_name
        self.output_dir: str = self._parse_result.output_dir
        self.compress_output: bool = self._parse_result.compress_output
        self.cover_image: str = self._parse_result.cover_image

    def get_settings(self) -> Settings:
        return {
            'legacy_dp': is_legacy_version(self.minecraft_version),
            'mix_mono': self.mix_mono,
            'name': self.package_name,
            'pack': absolute_path(self.cover_image),
            'skip_proc': self.use_parallel,
            'version': get_dp_rp_version(self.minecraft_version),
            'zip': self.compress_output
        }

    def get_music(self):
        with open(self.disc_entries_file, "r", encoding="utf8", newline='') as entries_file:
            csv_reader = reader(entries_file, delimiter=';')
            return DiscListContents(entries=[
                DiscListEntryContents(texture_file=absolute_path(row[0]),
                                      track_file=absolute_path(row[1]),
                                      title=row[2], internal_name=row[3],
                                      length=0, custom_model_data=0) for row in csv_reader])
