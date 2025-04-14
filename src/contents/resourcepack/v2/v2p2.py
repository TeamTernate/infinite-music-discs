# -*- coding: utf-8 -*-
#
#Infinite Music Discs resourcepack v2.2 contents
#Generation tool, datapack design, and resourcepack design by link2_thepast

from src.contents.resourcepack.v2.v2p1 import ResourcepackContents_v2p1



# pack namespace
# item/<track>.json
item_model_json = {
    'path': ['assets', '{pack_name}', 'items', '{entry.internal_name}.json'],
    'repeat': 'copy',
    'contents': \
{
    "model": {
        "type": "minecraft:model",
        "model": "{pack_name}:item/music_disc_{entry.internal_name}"
    }
}
}



# See src.contents.datapack.v2.v2p0 for info on this class structure
class ResourcepackContents_v2p2(ResourcepackContents_v2p1):

    min_pack_format = 55
    version_major = 2
    version_minor = 1

    def add_contents(self):
        super().add_contents()

        self.item_model_json = item_model_json
