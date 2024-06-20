# -*- coding: utf-8 -*-
#
#Infinite Music Discs contents concrete factory module
#Generation tool, datapack design, and resourcepack design by link2_thepast

# Virtual implementation of a concrete "pack factory"
# Pack factories are used to pick
#
# Pack factories are used to select between different DatapackContents or
#   ResourcepackContents. Uses pack_format to pick which version to use,
#   and returns an instance of the selected class
# If versions is sorted in ascending order (v0 -> v1 -> v2 -> etc)
#   then the factory will pick the latest datapack version compatible
#   with the given pack_format and return an instance of it
# See src.contents.datapack.v2.factory for an implementation example
class VirtualPackFactory():

    versions = []

    @property
    def min_pack_format(self):
        return self.versions[0].min_pack_format

    def get(self, pack_format: int):
        for v in self.versions:
            if v.min_pack_format <= pack_format:
                sel_version = v

        return sel_version()
