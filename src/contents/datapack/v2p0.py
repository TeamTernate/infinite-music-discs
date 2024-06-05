# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack v2.0 contents
#Generation tool, datapack design, and resourcepack design by link2_thepast

from src.contents.datapack.base import VirtualDatapackContents



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
        'function':'minecraft:set_nbt',
        'tag':'{{CustomModelData:{entry.custom_model_data}, HideFlags:32, display:{{Lore:[\"\\\"\\\\u00a77{entry.title}\\\"\"]}}}}'
    }]
}

creeper_normal_entries = [
    {
        'type':'minecraft:item',
        'functions':[{
                'function':'minecraft:set_count',
                'count':{'min':0.0, 'max':2.0, 'type':'minecraft:uniform'}
            }, {
                'function':'minecraft:looting_enchant',
                'count':{'min':0.0, 'max':1.0}
            }],
        'name':'minecraft:gunpowder'
    }
]

# creeper.json doesn't recursively format strings, since any string
#   formatting would have been done when the music disc loot table
#   entries were generated
creeper_json = {
    'path': ['data', 'minecraft', 'loot_tables', 'entities', 'creeper.json'],
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
            'entity':'killer'
        }]
    }]
}
}

# advancements
placed_disc = {
    'path': ['data', '{datapack_name}', 'advancements', 'placed_disc.json'],
    'repeat': 'single',
    'contents': \
{
  "criteria": {
    "placed_music_disc": {
      "trigger": "minecraft:item_used_on_block",
      "conditions": {
        "location": {
          "block": {
            "blocks": [ "minecraft:jukebox" ],
            "state": { "has_record":"true" }
          }
        },
        "item": {
          "tag": "minecraft:music_discs"
        }
      }
    }
  },
  "rewards": {
    "function": "{datapack_name}:on_placed_disc"
  }
}
}

placed_jukebox = {
    'path': ['data', '{datapack_name}', 'advancements', 'placed_jukebox.json'],
    'repeat': 'single',
    'contents': \
{
  "criteria": {
    "placed_jukebox": {
      "trigger": "minecraft:placed_block",
      "conditions": {
        "block": "minecraft:jukebox",
        "item": {
          "items": [ "minecraft:jukebox" ]
        }
      }
    }
  },
  "rewards": {
    "function": "{datapack_name}:on_placed_jukebox"
  }
}
}

# function tags
load = {
    'path': ['data', 'minecraft', 'tags', 'functions', 'load.json'],
    'repeat': 'single',
    'contents': \
{
    "values": [
        "{datapack_name}:setup_load"
    ]
}
}

tick = {
    'path': ['data', 'minecraft', 'tags', 'functions', 'tick.json'],
    'repeat': 'single',
    'contents': \
{
    "values": [
        "{datapack_name}:register_players_tick",
        "{datapack_name}:jukebox_event_tick"
    ]
}
}

# top-level functions
destroy_jukebox_marker = {
    'path': ['data', '{datapack_name}', 'functions', 'destroy_jukebox_marker.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
function {datapack_name}:stop
kill @s
"""
}

give_all_discs = {
    'path': ['data', '{datapack_name}', 'functions', 'give_all_discs.mcfunction'],
    'repeat': 'copy_within',
    'contents': \
"""
execute at @s run function {datapack_name}:give_{entry.internal_name}
"""
}

give_disc = {
    'path': ['data', '{datapack_name}', 'functions', 'give_{entry.internal_name}.mcfunction'],
    'repeat': 'copy',
    'contents': \
"""
execute at @s run summon item ~ ~ ~ {{Item:{{id:"minecraft:music_disc_11", Count:1b, tag:{{CustomModelData:{entry.custom_model_data}, HideFlags:32, display:{{Lore:["\\"\\\\u00a77{entry.title}\\""]}}}}}}}}
"""
}

help = {
    'path': ['data', '{datapack_name}', 'functions', 'help.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
tellraw @s {{"text":"\\nInfinite Music Discs Help", "color":"yellow", "bold":"true"}}
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"?", "color":"green", "bold":"true"}}, {{"text":"] A datapack & resourcepack that work together to add new music discs to Minecraft. Use ", "color":"gold"}}, {{"text":"the desktop app", "clickEvent":{{"action":"open_url", "value":"https://github.com/TeamTernate/infinite-music-discs"}}, "color":"aqua", "underlined":"true"}}, {{"text":" to generate your own packs and add your own music. Follow the project on ", "color":"gold"}}, {{"text":"CurseForge", "clickEvent":{{"action":"open_url", "value":"https://www.curseforge.com/minecraft/customization/infinite-music-discs"}}, "color":"aqua", "underlined":"true"}}, {{"text":" for update notifications!", "color":"gold"}}]
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"!", "color":"red", "bold":"true"}}, {{"text":"]", "color":"gold"}}, {{"text":" Install both the datapack and resourcepack or Infinite Music Discs will not work! The datapack goes in your world's datapack folder, and the resourcepack goes in your resourcepacks folder.", "color":"red"}}]
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":"true"}}, {{"text":"] To obtain custom discs in survival, get a skeleton to kill a creeper. The creeper will drop a music disc, and there's a chance it will be one of your custom music discs. All discs (including the vanilla discs) have an equal chance to drop. The more discs your pack adds, the harder it will be to get any particular disc. You might consider building a music disc farm.", "color":"gold"}}]
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":"true"}}, {{"text":"] Give yourself discs in creative with these commands:", "color":"gold"}}]
tellraw @s [{{"text":" - ", "color":"gold"}}, {{"text":"/function {datapack_name}:give_all_discs", "color":"yellow"}}]
tellraw @s [{{"text":" - ", "color":"gold"}}, {{"text":"/function {datapack_name}:give_<disc name>", "color":"yellow"}}]
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":"true"}}, {{"text":"] Hoppers and droppers can add/remove custom music discs from jukeboxes!", "color":"gold"}}]
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":"true"}}, {{"text":"] Custom tracks not playing? If you hear the 11 disc playing instead of your custom disc, try breaking and replacing the jukebox.", "color":"gold"}}]
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":"true"}}, {{"text":"] Is your music playing 'inside your head' instead of from the jukebox? Try checking the \\"{mix_mono_title}\\" setting when you generate your pack. Most music is stereo, and Minecraft plays stereo sounds globally instead of attaching them to a spot in the world.", "color":"gold"}}]
tellraw @s [{{"text":"\\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":"true"}}, {{"text":"] Still having problems? Use ", "color":"gold"}}, {{"text":"the issue tracker", "clickEvent":{{"action":"open_url", "value":"https://github.com/TeamTernate/infinite-music-discs/issues"}}, "color":"aqua", "underlined":"true"}}, {{"text":" to report bugs or ask for help.", "color":"gold"}}]
"""
}

jukebox_check_playing = {
    'path': ['data', '{datapack_name}', 'functions', 'jukebox_check_playing.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
execute as @s[tag=!imd_is_playing] if block ~ ~ ~ minecraft:jukebox{{IsPlaying:1b}} run function {datapack_name}:jukebox_on_play
execute as @s[tag=imd_is_playing] unless block ~ ~ ~ minecraft:jukebox{{IsPlaying:1b}} run function {datapack_name}:jukebox_on_stop
"""
}

jukebox_event_tick = {
    'path': ['data', '{datapack_name}', 'functions', 'jukebox_event_tick.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
execute as @e[type=marker,tag=imd_jukebox_marker] at @s unless block ~ ~ ~ minecraft:jukebox run function {datapack_name}:destroy_jukebox_marker
execute as @e[type=marker,tag=imd_jukebox_marker] at @s if block ~ ~ ~ minecraft:jukebox run function {datapack_name}:jukebox_check_playing
execute as @e[type=marker,tag=imd_jukebox_marker,tag=imd_is_playing,tag=imd_has_custom_disc] at @s run function {datapack_name}:jukebox_tick_timers
"""
}

jukebox_on_play = {
    'path': ['data', '{datapack_name}', 'functions', 'jukebox_on_play.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
tag @s add imd_is_playing
execute if data block ~ ~ ~ RecordItem.tag.CustomModelData run tag @s add imd_has_custom_disc
execute as @s[tag=imd_has_custom_disc] run function {datapack_name}:pre_play
"""
}

jukebox_on_stop = {
    'path': ['data', '{datapack_name}', 'functions', 'jukebox_on_stop.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
tag @s remove imd_is_playing
tag @s remove imd_has_custom_disc
tag @s remove imd_stopped_11
function {datapack_name}:stop
"""
}

jukebox_tick_timers = {
    'path': ['data', '{datapack_name}', 'functions', 'jukebox_tick_timers.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
execute as @s[scores={{imd_play_time=1..}}] run scoreboard players remove @s imd_play_time 1
execute as @s[scores={{imd_stop_11_time=1..}}] run scoreboard players remove @s imd_stop_11_time 1
execute as @s[scores={{imd_play_time=0}}] run data merge block ~ ~ ~ {{RecordStartTick:-999999L}}
execute as @s[scores={{imd_stop_11_time=0}},tag=!imd_stopped_11] run function {datapack_name}:stop_11
"""
}

on_placed_disc = {
    'path': ['data', '{datapack_name}', 'functions', 'on_placed_disc.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
advancement revoke @s only {datapack_name}:placed_disc
execute as @s run function {datapack_name}:raycast_start
"""
}

on_placed_jukebox = {
    'path': ['data', '{datapack_name}', 'functions', 'on_placed_jukebox.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
advancement revoke @s only {datapack_name}:placed_jukebox
execute as @s run function {datapack_name}:raycast_start
"""
}

play = {
    'path': ['data', '{datapack_name}', 'functions', 'play.mcfunction'],
    'repeat': 'copy_within', #single, copy_within, copy
    'contents': \
"""
execute if score @e[type=marker,tag=imd_jukebox_marker,distance=..0.1,limit=1] imd_disc_id matches {entry.custom_model_data} run function {datapack_name}:{entry.internal_name}/play
"""
}

play_duration = {
    'path': ['data', '{datapack_name}', 'functions', 'play_duration.mcfunction'],
    'repeat': 'copy_within',
    'contents': \
"""
execute if score @s imd_disc_id matches {entry.custom_model_data} run function {datapack_name}:{entry.internal_name}/play_duration
"""
}

pre_play = {
    'path': ['data', '{datapack_name}', 'functions', 'pre_play.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
execute store result score @s imd_disc_id run data get block ~ ~ ~ RecordItem.tag.CustomModelData
function {datapack_name}:play_duration
scoreboard players set @s imd_stop_11_time 3
function {datapack_name}:watchdog_reset_tickcount
execute as @a[distance=..64] run function {datapack_name}:register_jukebox_listener
"""
}

raycast_hit = {
    'path': ['data', '{datapack_name}', 'functions', 'raycast_hit.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
scoreboard players set @s imd_rc_steps 1
execute align xyz positioned ~0.5 ~0.5 ~0.5 unless entity @e[type=marker,tag=imd_jukebox_marker,distance=..0.1,limit=1] run function {datapack_name}:register_jukebox_marker
"""
}

raycast_start = {
    'path': ['data', '{datapack_name}', 'functions', 'raycast_start.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
scoreboard players set @s imd_rc_steps 1000
execute at @s anchored eyes positioned ^ ^ ^ run function {datapack_name}:raycast_step
"""
}

raycast_step = {
    'path': ['data', '{datapack_name}', 'functions', 'raycast_step.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
execute if block ~ ~ ~ minecraft:jukebox run function {datapack_name}:raycast_hit
scoreboard players remove @s imd_rc_steps 1
execute if score @s imd_rc_steps matches 1.. positioned ^ ^ ^0.005 run function {datapack_name}:raycast_step
"""
}

register_jukebox_listener = {
    'path': ['data', '{datapack_name}', 'functions', 'register_jukebox_listener.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
execute store result storage {datapack_name}:global tmp.Player int 1.0 run scoreboard players get @s imd_player_id
data modify entity @e[type=marker,tag=imd_jukebox_marker,distance=..0.1,limit=1] data.Listeners append from storage {datapack_name}:global tmp.Player
data modify entity @e[type=marker,tag=imd_jukebox_marker,distance=..0.1,limit=1] data.Listeners_11 append from storage {datapack_name}:global tmp.Player
function {datapack_name}:play
"""
}

register_jukebox_marker = {
    'path': ['data', '{datapack_name}', 'functions', 'register_jukebox_marker.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
summon marker ~ ~ ~ {{Tags:["imd_jukebox_marker"]}}
"""
}

register_player = {
    'path': ['data', '{datapack_name}', 'functions', 'register_player.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
execute store result score @s imd_player_id run scoreboard players add #imd_id_global imd_player_id 1
tag @s[scores={{imd_player_id=1..}}] add imd_has_id
"""
}

register_players_tick = {
    'path': ['data', '{datapack_name}', 'functions', 'register_players_tick.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
execute as @a[tag=!imd_has_id] run function {datapack_name}:register_player
"""
}

#note that v2 generator doesn't use ReplaceItemCommand for pre-1.17 compatibility
#  since v2 datapack is not compatible with pre-1.19.4 versions anyway
set_disc_track = {
    'path': ['data', '{datapack_name}', 'functions', 'set_disc_track.mcfunction'],
    'repeat': 'copy_within',
    'contents': \
"""
execute as @s[nbt={{SelectedItem:{{id:"minecraft:music_disc_11", tag:{{CustomModelData:{entry.custom_model_data}}}}}}}] run item replace entity @s weapon.mainhand with minecraft:music_disc_11{{CustomModelData:{entry.custom_model_data}, HideFlags:32, display:{{Lore:["\\"\\\\u00a77{entry.title}\\""]}}}}
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

advancement revoke @a only {datapack_name}:placed_disc
advancement revoke @a only {datapack_name}:placed_jukebox
tellraw @a [{{"text":"Infinite Music Discs {dp_version_str} by link2_thepast", "color":"gold"}}]
tellraw @a [{{"text":"Type ", "color":"gold"}}, {{"text":"/function {datapack_name}:help", "color":"yellow"}}, {{"text":" for help", "color":"gold"}}]
"""
}

stop = {
    'path': ['data', '{datapack_name}', 'functions', 'stop.mcfunction'],
    'repeat': 'copy_within',
    'contents': \
"""
execute if score @s imd_disc_id matches {entry.custom_model_data} run function {datapack_name}:{entry.internal_name}/stop
"""
}

stop_11 = {
    'path': ['data', '{datapack_name}', 'functions', 'stop_11.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
execute store result score @s imd_player_id run data get entity @s data.Listeners_11[0]
data remove entity @s data.Listeners_11[0]
execute as @a if score @s imd_player_id = @e[type=marker,tag=imd_jukebox_marker,distance=..0.1,limit=1] imd_player_id run stopsound @s record minecraft:music_disc.11
execute if data entity @s data.Listeners_11[0] run function {datapack_name}:stop_11
execute unless data entity @s data.Listeners_11[0] run tag @s add imd_stopped_11
"""
}

watchdog_reset_tickcount = {
    'path': ['data', '{datapack_name}', 'functions', 'watchdog_reset_tickcount.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
execute as @e[type=marker,tag=imd_jukebox_marker,tag=imd_is_playing,tag=imd_has_custom_disc] at @s run data merge block ~ ~ ~ {{TickCount:0L}}
schedule function {datapack_name}:watchdog_reset_tickcount 10s replace
"""
}

# per-disc functions
disc_play = {
    'path': ['data', '{datapack_name}', 'functions', '{entry.internal_name}', 'play.mcfunction'],
    'repeat': 'copy',
    'contents': \
"""
title @s actionbar {{"text":"Now Playing: {entry.title}", "color":"green"}}
playsound minecraft:music_disc.{entry.internal_name} record @s ~ ~ ~ 4 1
"""
}

disc_play_duration = {
    'path': ['data', '{datapack_name}', 'functions', '{entry.internal_name}', 'play_duration.mcfunction'],
    'repeat': 'copy',
    'contents': \
"""
scoreboard players set @s imd_play_time {entry.length}
"""
}

disc_stop = {
    'path': ['data', '{datapack_name}', 'functions', '{entry.internal_name}', 'stop.mcfunction'],
    'repeat': 'copy',
    'contents': \
"""
execute store result score @s imd_player_id run data get entity @s data.Listeners[0]
data remove entity @s data.Listeners[0]
execute as @a if score @s imd_player_id = @e[type=marker,tag=imd_jukebox_marker,distance=..0.1,limit=1] imd_player_id run stopsound @s record minecraft:music_disc.{entry.internal_name}
execute if data entity @s data.Listeners[0] run function {datapack_name}:{entry.internal_name}/stop
"""
}



# Datapack uses inheritance and the __dict__ attribute to easily change the
#   contents of files in future datapack versions. All instance attributes
#   are parsed from the instance's __dict__ and returned as a list for
#   the generator to iterate over and write files.
#
# Basically, any 'self.x' variables will be treated as datapack files. So
#   define the datapack file contents above, then assign them into the class
#   so the generator can see them (and pick the 'latest supported' via inheritance)
# Class attributes (like min_pack_format) have no special treatment.
#
# min_pack_format decides if this datapack version may be used for a
#   particular Minecraft version. If min_pack_format <= pack_format, then
#   the contents of this datapack version will override previous datapack
#   versions. Future datapack versions may override this one if their
#   min_pack_format requirement is met, and so on until the latest supported
#   datapack version is found and used.
class DatapackContents_v2p0(VirtualDatapackContents):

    min_pack_format = 12
    version_major = 2
    version_minor = 0

    #all datapack files except pack.mcmeta and creeper.json
    #those files are more complicated and require extra effort
    def add_contents(self):
        self.placed_disc = placed_disc
        self.placed_jukebox = placed_jukebox
        self.load = load
        self.tick = tick
        self.destroy_jukebox_marker = destroy_jukebox_marker
        self.give_all_discs = give_all_discs
        self.give_disc = give_disc
        self.help = help
        self.jukebox_check_playing = jukebox_check_playing
        self.jukebox_event_tick = jukebox_event_tick
        self.jukebox_on_play = jukebox_on_play
        self.jukebox_on_stop = jukebox_on_stop
        self.jukebox_tick_timers = jukebox_tick_timers
        self.on_placed_disc = on_placed_disc
        self.on_placed_jukebox = on_placed_jukebox
        self.pack_mcmeta = pack_mcmeta
        self.play = play
        self.play_duration = play_duration
        self.pre_play = pre_play
        self.raycast_hit = raycast_hit
        self.raycast_start = raycast_start
        self.raycast_step = raycast_step
        self.register_jukebox_listener = register_jukebox_listener
        self.register_jukebox_marker = register_jukebox_marker
        self.register_player = register_player
        self.register_players_tick = register_players_tick
        self.set_disc_track = set_disc_track
        self.setup_load = setup_load
        self.stop = stop
        self.stop_11 = stop_11
        self.watchdog_reset_tickcount = watchdog_reset_tickcount
        self.disc_play = disc_play
        self.disc_play_duration = disc_play_duration
        self.disc_stop = disc_stop

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


