# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack v3.3 contents
#Generation tool, datapack design, and resourcepack design by link2_thepast

from src.contents.datapack.v3.v3p2 import DatapackContents_v3p2



# per-disc functions
disc_give = {
    'path': ['data', '{pack_name}', 'function', 'give', '{entry.internal_name}.mcfunction'],
    'repeat': 'copy',
    'contents': \
"""
execute at @s run summon item ~ ~ ~ {{Item:{{id:"minecraft:music_disc_11",count:1b ,components:{{item_model:"{pack_name}:{entry.internal_name}",jukebox_playable:"{pack_name}:{entry.internal_name}"}}}}}}
"""
}



help = {
    'path': ['data', '{pack_name}', 'function', 'help.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
tellraw @s {{"text":"\\nInfinite Music Discs Help", "color":"yellow", "bold":true}}
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"?", "color":"green", "bold":true}}, {{"text":"] A datapack & resourcepack that work together to add new music discs to Minecraft. Use ", "color":"gold"}}, {{"text":"the desktop app", "click_event":{{"action":"open_url", "url":"https://github.com/TeamTernate/infinite-music-discs"}}, "color":"aqua", "underlined":true}}, {{"text":" to generate your own packs and add your own music. Follow the project on ", "color":"gold"}}, {{"text":"CurseForge", "click_event":{{"action":"open_url", "url":"https://www.curseforge.com/minecraft/customization/infinite-music-discs"}}, "color":"aqua", "underlined":true}}, {{"text":" for update notifications!", "color":"gold"}}]
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"!", "color":"red", "bold":true}}, {{"text":"]", "color":"gold"}}, {{"text":" Install both the datapack and resourcepack or Infinite Music Discs will not work! The datapack goes in your world's datapack folder, and the resourcepack goes in your resourcepacks folder.", "color":"red"}}]
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":true}}, {{"text":"] To obtain custom discs in survival, get a skeleton to kill a creeper. The creeper will drop a music disc, and there's a chance it will be one of your custom music discs. All discs (including the vanilla discs) have an equal chance to drop. The more discs your pack adds, the harder it will be to get any particular disc. You might consider building a music disc farm.", "color":"gold"}}]
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":true}}, {{"text":"] Give yourself discs in creative with these commands:", "color":"gold"}}]
tellraw @s [{{"text":" - ", "color":"gold"}}, {{"text":"/function minecraft_movie:give_all_discs", "color":"yellow"}}]
tellraw @s [{{"text":" - ", "color":"gold"}}, {{"text":"/function minecraft_movie:give/<disc name>", "color":"yellow"}}]
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":true}}, {{"text":"] Hoppers and droppers can add/remove custom music discs from jukeboxes!", "color":"gold"}}]
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":true}}, {{"text":"] Is your music playing 'inside your head' instead of from the jukebox? Try checking the \"Play tracks from the jukebox block\" setting when you generate your pack. Most music is stereo, and Minecraft plays stereo sounds globally instead of attaching them to a spot in the world.", "color":"gold"}}]
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":true}}, {{"text":"] Still having problems? Use ", "color":"gold"}}, {{"text":"the issue tracker", "click_event":{{"action":"open_url", "url":"https://github.com/TeamTernate/infinite-music-discs/issues"}}, "color":"aqua", "underlined":true}}, {{"text":" to report bugs or ask for help.", "color":"gold"}}]
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
class DatapackContents_v3p3(DatapackContents_v3p2):

    min_pack_format = 71
    version_major = 3
    version_minor = 1

    def add_contents(self):
        super().add_contents()

        self.help = help
        self.disc_give = disc_give

    def get_creeper_music_entry_custom(self):
        return creeper_music_entry_custom
