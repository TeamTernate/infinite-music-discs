# -*- coding: utf-8 -*-
#
#Infinite Music Discs resourcepack v2.2 contents
#Generation tool, datapack design, and resourcepack design by link2_thepast

from src.contents.resourcepack.v2.v2p1 import ResourcepackContents_v2p1

# pack.mcmeta
pack_mcmeta = {
    'path': ['pack.mcmeta'],
    'repeat': 'single',
    'contents': \
{
    "pack": {
        "min_format": '(int){pack_format}',
        "max_format": '(int){max_pack_format}',
        "description": "Adds {rp_num_discs} custom music discs"
    }
}
}

# See src.contents.datapack.v2.v2p0 for info on this class structure
class ResourcepackContents_v2p2(ResourcepackContents_v2p1):

    min_pack_format = 69
    max_pack_format = 999
    version_major = 2
    version_minor = 1

    def add_contents(self):
        super().add_contents()

        self.pack_mcmeta = pack_mcmeta
