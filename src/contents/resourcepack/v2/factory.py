# -*- coding: utf-8 -*-
#
#Infinite Music Discs resourcepack contents factory module
#Generation tool, datapack design, and resourcepack design by link2_thepast

from src.contents.resourcepack.v2.v2p0 import ResourcepackContents_v2p0

class Resourcepackv2Factory():

    versions = [
        ResourcepackContents_v2p0
    ]

    @property
    def min_pack_format(self):
        return self.versions[0].min_pack_format

    def get(self, pack_format: int):
        for v in self.versions:
            if v.min_pack_format <= pack_format:
                sel_version = v

        return sel_version()
