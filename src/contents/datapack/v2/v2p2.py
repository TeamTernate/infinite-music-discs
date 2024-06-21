# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack v2.2 contents
#Generation tool, datapack design, and resourcepack design by link2_thepast

from src.contents.datapack.v2.v2p1 import DatapackContents_v2p1



# function tags
tick = {
    'path': ['data', 'minecraft', 'tags', 'functions', 'tick.json'],
    'repeat': 'single',
    'contents': \
{
    "values": [
        "{datapack_name}:watchdog_setup_load_tick",
        "{datapack_name}:register_players_tick",
        "{datapack_name}:jukebox_event_tick"
    ]
}
}

# top-level functions

help = {
    'path': ['data', '{datapack_name}', 'functions', 'help.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
tellraw @s {{"text":"\\nInfinite Music Discs Help", "color":"yellow", "bold":true}}
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"?", "color":"green", "bold":true}}, {{"text":"] A datapack & resourcepack that work together to add new music discs to Minecraft. Use ", "color":"gold"}}, {{"text":"the desktop app", "clickEvent":{{"action":"open_url", "value":"https://github.com/TeamTernate/infinite-music-discs"}}, "color":"aqua", "underlined":true}}, {{"text":" to generate your own packs and add your own music. Follow the project on ", "color":"gold"}}, {{"text":"CurseForge", "clickEvent":{{"action":"open_url", "value":"https://www.curseforge.com/minecraft/customization/infinite-music-discs"}}, "color":"aqua", "underlined":true}}, {{"text":" for update notifications!", "color":"gold"}}]
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"!", "color":"red", "bold":true}}, {{"text":"]", "color":"gold"}}, {{"text":" Install both the datapack and resourcepack or Infinite Music Discs will not work! The datapack goes in your world's datapack folder, and the resourcepack goes in your resourcepacks folder.", "color":"red"}}]
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":true}}, {{"text":"] To obtain custom discs in survival, get a skeleton to kill a creeper. The creeper will drop a music disc, and there's a chance it will be one of your custom music discs. All discs (including the vanilla discs) have an equal chance to drop. The more discs your pack adds, the harder it will be to get any particular disc. You might consider building a music disc farm.", "color":"gold"}}]
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":true}}, {{"text":"] Give yourself discs in creative with these commands:", "color":"gold"}}]
tellraw @s [{{"text":" - ", "color":"gold"}}, {{"text":"/function {datapack_name}:give_all_discs", "color":"yellow"}}]
tellraw @s [{{"text":" - ", "color":"gold"}}, {{"text":"/function {datapack_name}:give_<disc name>", "color":"yellow"}}]
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":true}}, {{"text":"] Hoppers and droppers can add/remove custom music discs from jukeboxes!", "color":"gold"}}]
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":true}}, {{"text":"] Custom tracks not playing? If you hear the 11 disc playing instead of your custom disc, try breaking and replacing the jukebox.", "color":"gold"}}]
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":true}}, {{"text":"] Is your music playing 'inside your head' instead of from the jukebox? Try checking the \\"{mix_mono_title}\\" setting when you generate your pack. Most music is stereo, and Minecraft plays stereo sounds globally instead of attaching them to a spot in the world.", "color":"gold"}}]
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":true}}, {{"text":"] Still having problems? Use ", "color":"gold"}}, {{"text":"the issue tracker", "clickEvent":{{"action":"open_url", "value":"https://github.com/TeamTernate/infinite-music-discs/issues"}}, "color":"aqua", "underlined":true}}, {{"text":" to report bugs or ask for help.", "color":"gold"}}]
"""
}

setup_load = {
    'path': ['data', '{datapack_name}', 'functions', 'setup_load.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
scoreboard objectives add imd_player_id dummy
scoreboard objectives add imd_disc_id dummy
scoreboard objectives add imd_rc_steps dummy
scoreboard objectives add imd_play_time dummy
scoreboard objectives add imd_stop_11_time dummy

scoreboard objectives add imd_is_loaded dummy
scoreboard players set #imd_is_loaded imd_is_loaded 1

advancement revoke @a only {datapack_name}:placed_disc
advancement revoke @a only {datapack_name}:placed_jukebox
tellraw @a [{{"text":"Infinite Music Discs {dp_version_str} by link2_thepast", "color":"gold"}}]
tellraw @a [{{"text":"Type ", "color":"gold"}}, {{"text":"/function {datapack_name}:help", "color":"yellow"}}, {{"text":" for help", "color":"gold"}}]
"""
}

watchdog_setup_load_tick = {
    'path': ['data', '{datapack_name}', 'functions', 'watchdog_setup_load_tick.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
scoreboard objectives add imd_is_loaded dummy
execute unless score #imd_is_loaded imd_is_loaded matches 1 run function {datapack_name}:setup_load
"""
}



# See src.contents.datapack.v2p0 for info on this class structure
class DatapackContents_v2p2(DatapackContents_v2p1):

    min_pack_format = 26
    version_major = 2
    version_minor = 2

    def add_contents(self):
        super().add_contents()

        self.tick = tick
        self.help = help
        self.setup_load = setup_load
        self.watchdog_setup_load_tick = watchdog_setup_load_tick


