# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack v2.3 contents
#Generation tool, datapack design, and resourcepack design by link2_thepast

from src.contents.datapack.v2.v2p2 import DatapackContents_v2p2



# creeper loot table
# custom_model_data must be specially encoded - datapack formatter
#   will see the "(int)" prefix and cast it to an integer
#   after string formatting
creeper_music_entry_custom = {
    'type':'minecraft:item',
    'weight':1,
    'name':'minecraft:music_disc_11',
    'functions':[{
        'function':'minecraft:set_components',
        'components':{
            'minecraft:custom_model_data':'(int){entry.custom_model_data}',
            'minecraft:hide_additional_tooltip':{},
            'minecraft:lore':[
                '{{\"text\":\"{entry.title}\", \"color\":\"gray\", \"italic\":false}}'
            ]
        }
    }]
}



# top-level functions
give_disc = {
    'path': ['data', '{datapack_name}', 'functions', 'give_{entry.internal_name}.mcfunction'],
    'repeat': 'copy',
    'contents': \
"""
execute at @s run summon item ~ ~ ~ {{Item:{{id:"minecraft:music_disc_11", Count:1b, components:{{custom_model_data:{entry.custom_model_data}, hide_additional_tooltip:{{}}, lore:["{{\\"text\\":\\"{entry.title}\\", \\"color\\":\\"gray\\", \\"italic\\":false}}"]}}}}}}
"""
}

jukebox_on_play = {
    'path': ['data', '{datapack_name}', 'functions', 'jukebox_on_play.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
tag @s add imd_is_playing
execute if data block ~ ~ ~ RecordItem.components.minecraft:custom_model_data run tag @s add imd_has_custom_disc
execute as @s[tag=imd_has_custom_disc] run function {datapack_name}:pre_play
"""
}

pre_play = {
    'path': ['data', '{datapack_name}', 'functions', 'pre_play.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
execute store result score @s imd_disc_id run data get block ~ ~ ~ RecordItem.components.minecraft:custom_model_data
function {datapack_name}:play_duration
scoreboard players set @s imd_stop_11_time 3
function {datapack_name}:watchdog_reset_tickcount
execute as @a[distance=..64] run function {datapack_name}:register_jukebox_listener
"""
}

set_disc_track = {
    'path': ['data', '{datapack_name}', 'functions', 'set_disc_track.mcfunction'],
    'repeat': 'copy_within',
    'contents': \
"""
execute as @s if items entity @s weapon.mainhand minecraft:music_disc_11[custom_model_data={entry.custom_model_data}] run item replace entity @s weapon.mainhand with minecraft:music_disc_11[custom_model_data={entry.custom_model_data},hide_additional_tooltip={{}},lore=["{{\\"text\\":\\"{entry.title}\\", \\"color\\":\\"gray\\", \\"italic\\":false}}"]]
"""
}



# See src.contents.datapack.v2p0 for info on this class structure
class DatapackContents_v2p3(DatapackContents_v2p2):

    min_pack_format = 41
    version_major = 2
    version_minor = 3

    def add_contents(self):
        super().add_contents()

        self.give_disc = give_disc
        self.jukebox_on_play = jukebox_on_play
        self.pre_play = pre_play
        self.set_disc_track = set_disc_track

    #creeper.json
    def get_creeper_music_entry_custom(self):
        return creeper_music_entry_custom


