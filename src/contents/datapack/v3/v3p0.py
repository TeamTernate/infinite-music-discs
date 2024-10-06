# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack v3.0 contents
#Generation tool, datapack design, and resourcepack design by link2_thepast

from src.contents.base import VirtualPackContents



# pack.mcmeta
# pack_format must be specially encoded - datapack formatter
#   will see the "(int)" prefix and cast it to an integer
#   after string formatting
pack_mcmeta = {
    'path': ['pack.mcmeta'],
    'repeat': 'single',
    'contents': \
{
    "pack": {
        "pack_format": '(int){pack_format}',
        "description": "Adds {dp_num_discs} custom music discs"
    }
}
}

# creeper loot table
# custom_model_data must be specially encoded - datapack formatter
#   will see the "(int)" prefix and cast it to an integer
#   after string formatting
creeper_music_entries = []

creeper_music_entry_base = {
    'type': 'minecraft:tag',
    'weight': 1,
    'name': 'minecraft:creeper_drop_music_discs',
    'expand': True
}

creeper_music_entry_custom = {
    'type':'minecraft:item',
    'weight':1,
    'name':'minecraft:music_disc_11',
    'functions':[{
        'function':'minecraft:set_components',
        'components':{
            'minecraft:custom_model_data':'(int){entry.custom_model_data}',
            'minecraft:jukebox_playable':{
                'song':'{pack_name}:{entry.internal_name}'
            }
        }
    }]
}

creeper_normal_entries = [
    {
        'type': 'minecraft:item',
        'functions': [
        {
            'add': False,
            'count': {
                'type': 'minecraft:uniform',
                'max': 2.0,
                'min': 0.0
            },
            'function': 'minecraft:set_count'
        },
        {
            'count': {
                'type': 'minecraft:uniform',
                'max': 1.0,
                'min': 0.0
            },
            'enchantment': 'minecraft:looting',
            'function': 'minecraft:enchanted_count_increase'
        }
        ],
        'name': 'minecraft:gunpowder'
    }
]

# creeper.json doesn't recursively format strings, since any string
#   formatting would have been done when the music disc loot table
#   entries were generated
creeper_json = {
    'path': ['data', 'minecraft', 'loot_table', 'entities', 'creeper.json'],
    'repeat': 'single',
    'format_contents': False,
    'contents': \
{
    'type':'minecraft:entity',
    'pools':[
        {'rolls':1, 'entries':creeper_normal_entries},
        {'rolls':1, 'entries':creeper_music_entries, 'conditions':[{
            'condition':'minecraft:entity_properties',
            'predicate':{'type':'#minecraft:skeletons'},
            'entity':'attacker'
        }]
    }],
    'random_sequence':'minecraft:entities/creeper'
}
}

# jukebox_song files
jukebox_song = {
    'path': ['data', '{pack_name}', 'jukebox_song', '{entry.internal_name}.json'],
    'repeat': 'copy',
    'contents': \
{
    "comparator_output": 11,
    "description": "{entry.title}",
    "length_in_seconds": "(float){entry.length_s}",
    "sound_event": {
        "sound_id": "{pack_name}:music_disc.{entry.internal_name}",
        "range": 64.0
    }
}
}

# function tags
load = {
    'path': ['data', 'minecraft', 'tags', 'function', 'load.json'],
    'repeat': 'single',
    'contents': \
{
    "values": [
        "{pack_name}:setup_load"
    ]
}
}

# top-level functions
give_all_discs = {
    'path': ['data', '{pack_name}', 'function', 'give_all_discs.mcfunction'],
    'repeat': 'copy_within',
    'contents': \
"""
execute at @s run function {pack_name}:give/{entry.internal_name}
"""
}

help = {
    'path': ['data', '{pack_name}', 'function', 'help.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
tellraw @s {{"text":"\\nInfinite Music Discs Help", "color":"yellow", "bold":true}}
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"?", "color":"green", "bold":true}}, {{"text":"] A datapack & resourcepack that work together to add new music discs to Minecraft. Use ", "color":"gold"}}, {{"text":"the desktop app", "clickEvent":{{"action":"open_url", "value":"https://github.com/TeamTernate/infinite-music-discs"}}, "color":"aqua", "underlined":true}}, {{"text":" to generate your own packs and add your own music. Follow the project on ", "color":"gold"}}, {{"text":"CurseForge", "clickEvent":{{"action":"open_url", "value":"https://www.curseforge.com/minecraft/customization/infinite-music-discs"}}, "color":"aqua", "underlined":true}}, {{"text":" for update notifications!", "color":"gold"}}]
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"!", "color":"red", "bold":true}}, {{"text":"]", "color":"gold"}}, {{"text":" Install both the datapack and resourcepack or Infinite Music Discs will not work! The datapack goes in your world's datapack folder, and the resourcepack goes in your resourcepacks folder.", "color":"red"}}]
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":true}}, {{"text":"] To obtain custom discs in survival, get a skeleton to kill a creeper. The creeper will drop a music disc, and there's a chance it will be one of your custom music discs. All discs (including the vanilla discs) have an equal chance to drop. The more discs your pack adds, the harder it will be to get any particular disc. You might consider building a music disc farm.", "color":"gold"}}]
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":true}}, {{"text":"] Give yourself discs in creative with these commands:", "color":"gold"}}]
tellraw @s [{{"text":" - ", "color":"gold"}}, {{"text":"/function {pack_name}:give_all_discs", "color":"yellow"}}]
tellraw @s [{{"text":" - ", "color":"gold"}}, {{"text":"/function {pack_name}:give/<disc name>", "color":"yellow"}}]
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":true}}, {{"text":"] Hoppers and droppers can add/remove custom music discs from jukeboxes!", "color":"gold"}}]
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":true}}, {{"text":"] Is your music playing 'inside your head' instead of from the jukebox? Try checking the \\"{mix_mono_title}\\" setting when you generate your pack. Most music is stereo, and Minecraft plays stereo sounds globally instead of attaching them to a spot in the world.", "color":"gold"}}]
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":true}}, {{"text":"] Still having problems? Use ", "color":"gold"}}, {{"text":"the issue tracker", "clickEvent":{{"action":"open_url", "value":"https://github.com/TeamTernate/infinite-music-discs/issues"}}, "color":"aqua", "underlined":true}}, {{"text":" to report bugs or ask for help.", "color":"gold"}}]
"""
}

setup_load = {
    'path': ['data', '{pack_name}', 'function', 'setup_load.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
tellraw @a [{{"text":"Infinite Music Discs {dp_version_str} by link2_thepast", "color":"gold"}}]
tellraw @a [{{"text":"Type ", "color":"gold"}}, {{"text":"/function {pack_name}:help", "color":"yellow"}}, {{"text":" for help", "color":"gold"}}]
"""
}

# per-disc functions
disc_give = {
    'path': ['data', '{pack_name}', 'function', 'give', '{entry.internal_name}.mcfunction'],
    'repeat': 'copy',
    'contents': \
"""
execute at @s run summon item ~ ~ ~ {{Item:{{id:"minecraft:music_disc_11", Count:1b, components:{{custom_model_data:{entry.custom_model_data}, jukebox_playable:{{song:"{pack_name}:{entry.internal_name}"}}}}}}}}
"""
}



# See src.contents.datapack.v2.v2p0 for info on this class structure
class DatapackContents_v3p0(VirtualPackContents):

    min_pack_format = 48
    version_major = 3
    version_minor = 0

    #all datapack files except creeper.json
    #that file is more complicated and require extra effort
    def add_contents(self):
        self.give_all_discs = give_all_discs
        self.help = help
        self.jukebox_song = jukebox_song
        self.load = load
        self.pack_mcmeta = pack_mcmeta
        self.setup_load = setup_load
        self.disc_give = disc_give

    @property
    def version_str(self):
        return f"v{self.version_major}.{self.version_minor}"

    #creeper.json
    def get_creeper_music_entry_base(self):
        return creeper_music_entry_base

    def get_creeper_music_entry_custom(self):
        return creeper_music_entry_custom

    def get_creeper_json(self, creeper_music_entries: list):
        #reach inside and set the music disc entries manually since it's
        #  hard to elegantly generate this file
        creeper_json['contents']['pools'][1]['entries'] = creeper_music_entries
        return creeper_json


