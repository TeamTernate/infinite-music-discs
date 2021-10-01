import json
import os
from typing import List

data = [
    {
        "pack_format": 5,
        "game_versions": "1.15-1.16.1"
    },
    {
        "pack_format": 6,
        "game_versions": "1.16.2-1.16.5"
    },
    {
        "pack_format": 7,
        "game_versions": "1.17"
    },
    {
        "pack_format": 8,
        "game_versions": "1.18+"
    }
]


class PackFormat:
    def __init__(self, pack_format: int, game_versions: str):
        self.pack_format = pack_format
        self.game_versions = game_versions


def get_pack_formats() -> List[PackFormat]:
    pack_formats = []
    for elm in data:
        pack_format = elm['pack_format']
        game_versions = elm['game_versions']
        pack_formats.append(PackFormat(pack_format, game_versions))

    return pack_formats


def get_game_versions():
    pack_formats = get_pack_formats()
    versions = []
    for pformat in pack_formats:
        versions.append(pformat.game_versions)
    return versions


def get_pack_format_by_version(game_version):
    pack_formats = get_pack_formats()
    for pformat in pack_formats:
        if pformat.game_versions == game_version:
            return pformat.pack_format
    return 0
