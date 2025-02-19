# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack v3.1 contents
#Generation tool, datapack design, and resourcepack design by link2_thepast

from src.contents.datapack.v3.v3p0 import DatapackContents_v3p0



# per-disc functions
disc_give = {
    'path': ['data', '{pack_name}', 'function', 'give', '{entry.internal_name}.mcfunction'],
    'repeat': 'copy',
    'contents': \
"""
execute at @s run summon item ~ ~ ~ {{Item:{{id:"minecraft:music_disc_11", Count:1b, components:{{"minecraft:item_model":"{pack_name}:{entry.internal_name}", "minecraft:jukebox_playable":{{song:"{pack_name}:{entry.internal_name}"}}}}}}}}
"""
}



# See src.contents.datapack.v2.v2p0 for info on this class structure
class DatapackContents_v3p1(DatapackContents_v3p0):

    min_pack_format = 61
    version_major = 3
    version_minor = 1

    def add_contents(self):
        super().add_contents()

        self.disc_give = disc_give
