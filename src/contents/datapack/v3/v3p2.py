# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack v3.2 contents
#Generation tool, datapack design, and resourcepack design by link2_thepast

from src.contents.datapack.v3.v3p1 import DatapackContents_v3p1



# per-disc functions
disc_give = {
    'path': ['data', '{pack_name}', 'function', 'give', '{entry.internal_name}.mcfunction'],
    'repeat': 'copy',
    'contents': \
"""
execute at @s run summon item ~ ~ ~ {{Item:{{id:"minecraft:music_disc_11", Count:1b, components:{{"minecraft:item_model":"{pack_name}:{entry.internal_name}", "minecraft:jukebox_playable":"{pack_name}:{entry.internal_name}"}}}}}}
"""
}



# creeper loot table
creeper_music_entry_custom = {
    'type':'minecraft:item',
    'weight':1,
    'name':'minecraft:music_disc_11',
    'functions':[{
        'function':'minecraft:set_components',
        'components':{
            'minecraft:item_model':'{pack_name}:{entry.internal_name}',
            'minecraft:jukebox_playable':'{pack_name}:{entry.internal_name}'
        }
    }]
}



# See src.contents.datapack.v2.v2p0 for info on this class structure
class DatapackContents_v3p2(DatapackContents_v3p1):

    min_pack_format = 64
    version_major = 3
    version_minor = 1

    def add_contents(self):
        super().add_contents()

        self.disc_give = disc_give

    def get_creeper_music_entry_custom(self):
        return creeper_music_entry_custom
