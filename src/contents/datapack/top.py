# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack contents factory module
#Generation tool, datapack design, and resourcepack design by link2_thepast

from src.contents.datapack.v2p0 import DatapackContents_v2p0
from src.contents.datapack.v2p1 import DatapackContents_v2p1

# Static factory class to select between different DatapackContents child
#   classes. Uses pack_format to pick which datapack version to use
class DatapackContentsGenerator():

    versions = [
        DatapackContents_v2p0,
        DatapackContents_v2p1
    ]

    def get_dp(pack_format: int):
        for v in DatapackContentsGenerator.versions:
            if v.min_pack_format <= pack_format:
                sel_version = v

        return sel_version()
