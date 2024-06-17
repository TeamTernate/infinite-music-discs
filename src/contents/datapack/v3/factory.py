# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack contents factory module
#Generation tool, datapack design, and resourcepack design by link2_thepast

from src.contents.datapack.v3.v3p0 import DatapackContents_v3p0

# Factory to select between different DatapackContents child
#   classes. Uses pack_format to pick which datapack version to use
# If versions is sorted in ascending order (v0 -> v1 -> v2 -> etc)
#   then the factory will pick the latest datapack version compatible
#   with the given pack_format and return an instance of it
class Datapackv3Factory():

    versions = [
        DatapackContents_v3p0
    ]

    @property
    def min_pack_format(self):
        return self.versions[0].min_pack_format

    def get(self, pack_format: int):
        for v in self.versions:
            if v.min_pack_format <= pack_format:
                sel_version = v

        return sel_version()
