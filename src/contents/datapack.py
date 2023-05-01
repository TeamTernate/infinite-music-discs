# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack file contents module
#Generation tool, datapack design, and resourcepack design by link2_thepast
#
#Stores the contents of every file in the datapack in a templated form
#  to make generation easy. Datapack generator will try to create a
#  file from every object in file_list

# pack.mcmeta
pack_mcmeta = {
    'path': ['{datapack_name}', 'pack.mcmeta'],
    'repeat': 'single',
    'contents': \
{
    "pack": {
        "pack_format": -1,
        "description": "Adds {dp_num_discs} custom music discs"
    }
}
}

# creeper loot table
creeper_music_entries = [
    {'type':'minecraft:tag', 'weight':1, 'name':'minecraft:creeper_drop_music_discs', 'expand':True}
]

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
    'path': ['{datapack_name}', 'data', 'minecraft', 'loot_tables', 'entities', 'creeper.json'],
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
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'advancements', 'placed_disc.json'],
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
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'advancements', 'placed_jukebox.json'],
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
    'path': ['{datapack_name}', 'data', 'minecraft', 'tags', 'functions', 'load.json'],
    'repeat': 'single',
    'contents': \
{
    "values": [
        "{datapack_name}:setup_load"
    ]
}
}

tick = {
    'path': ['{datapack_name}', 'data', 'minecraft', 'tags', 'functions', 'tick.json'],
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
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', 'destroy_jukebox_marker.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
function {datapack_name}:stop
kill @s
"""
}

give_all_discs = {
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', 'give_all_discs.mcfunction'],
    'repeat': 'copy_within',
    'contents': \
"""
execute at @s run function {datapack_name}:give_{entry.internal_name}
"""
}

give_disc = {
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', 'give_{entry.internal_name}.mcfunction'],
    'repeat': 'copy',
    'contents': \
"""
execute at @s run summon item ~ ~ ~ {{Item:{{id:"minecraft:music_disc_11", Count:1b, tag:{{CustomModelData:{entry.custom_model_data}, HideFlags:32, display:{{Lore:["\\"\\\\u00a77{entry.title}\\""]}}}}}}}}
"""
}

help = {
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', 'help.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
tellraw @s {{"text":"\nInfinite Music Discs Help", "color":"yellow", "bold":"true"}}
tellraw @s [{{"text":"\n[", "color":"gold"}}, {{"text":"?", "color":"green", "bold":"true"}}, {{"text":"] A datapack & resourcepack that work together to add new music discs to Minecraft. Use ", "color":"gold"}}, {{"text":"the desktop app", "clickEvent":{{"action":"open_url", "value":"https://github.com/TeamTernate/infinite-music-discs"}}, "color":"aqua", "underlined":"true"}}, {{"text":" to generate your own packs and add your own music. Follow the project on ", "color":"gold"}}, {{"text":"CurseForge", "clickEvent":{{"action":"open_url", "value":"https://www.curseforge.com/minecraft/customization/infinite-music-discs"}}, "color":"aqua", "underlined":"true"}}, {{"text":" for update notifications!", "color":"gold"}}]
tellraw @s [{{"text":"\n[", "color":"gold"}}, {{"text":"!", "color":"red", "bold":"true"}}, {{"text":"]", "color":"gold"}}, {{"text":" Install both the datapack and resourcepack or Infinite Music Discs will not work! The datapack goes in your world's datapack folder, and the resourcepack goes in your resourcepacks folder.", "color":"red"}}]
tellraw @s [{{"text":"\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":"true"}}, {{"text":"] To obtain custom discs in survival, get a skeleton to kill a creeper. The creeper will drop a music disc, and there's a chance it will be one of your custom music discs. All discs (including the vanilla discs) have an equal chance to drop. The more discs your pack adds, the harder it will be to get any particular disc. You might consider building a music disc farm.", "color":"gold"}}]
tellraw @s [{{"text":"\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":"true"}}, {{"text":"] Give yourself discs in creative with these commands:", "color":"gold"}}]
tellraw @s [{{"text":" - ", "color":"gold"}}, {{"text":"/function {datapack_name}:give_all_discs", "color":"yellow"}}]
tellraw @s [{{"text":" - ", "color":"gold"}}, {{"text":"/function {datapack_name}:give_<disc name>", "color":"yellow"}}]
tellraw @s [{{"text":"\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":"true"}}, {{"text":"] Hoppers and droppers can play custom music discs just like vanilla discs. If discs are not playing, try breaking and replacing the jukebox.", "color":"gold"}}]
tellraw @s [{{"text":"\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":"true"}}, {{"text":"] Is your music playing 'inside your head' instead of from the jukebox? Try checking the \"Mix stereo tracks to mono\" setting when you generate your pack. Most music is stereo, and Minecraft plays stereo sounds globally instead of attaching them to a spot in the world.", "color":"gold"}}]
tellraw @s [{{"text":"\n[", "color":"gold"}}, {{"text":"i", "color":"aqua", "bold":"true"}}, {{"text":"] Still having problems? Use ", "color":"gold"}}, {{"text":"the issue tracker", "clickEvent":{{"action":"open_url", "value":"https://github.com/TeamTernate/infinite-music-discs/issues"}}, "color":"aqua", "underlined":"true"}}, {{"text":" to report bugs or ask for help.", "color":"gold"}}]
"""
}

jukebox_check_playing = {
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', 'jukebox_check_playing.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
execute as @s[tag=!imd_is_playing] if block ~ ~ ~ minecraft:jukebox{{IsPlaying:1b}} run function {datapack_name}:jukebox_on_play
execute as @s[tag=imd_is_playing] unless block ~ ~ ~ minecraft:jukebox{{IsPlaying:1b}} run function {datapack_name}:jukebox_on_stop
"""
}

jukebox_event_tick = {
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', 'jukebox_event_tick.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
execute as @e[type=marker,tag=imd_jukebox_marker] at @s unless block ~ ~ ~ minecraft:jukebox run function {datapack_name}:destroy_jukebox_marker
execute as @e[type=marker,tag=imd_jukebox_marker] at @s if block ~ ~ ~ minecraft:jukebox run function {datapack_name}:jukebox_check_playing
execute as @e[type=marker,tag=imd_jukebox_marker,tag=imd_is_playing,tag=imd_has_custom_disc] at @s run function {datapack_name}:jukebox_tick_timers
"""
}

jukebox_on_play = {
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', 'jukebox_on_play.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
tag @s add imd_is_playing
execute if data block ~ ~ ~ RecordItem.tag.CustomModelData run tag @s add imd_has_custom_disc
execute as @s[tag=imd_has_custom_disc] run function {datapack_name}:pre_play
"""
}

jukebox_on_stop = {
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', 'jukebox_on_stop.mcfunction'],
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
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', 'jukebox_tick_timers.mcfunction'],
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
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', 'on_placed_disc.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
advancement revoke @s only {datapack_name}:placed_disc
execute as @s run function {datapack_name}:raycast_start
"""
}

on_placed_jukebox = {
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', 'on_placed_jukebox.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
advancement revoke @s only {datapack_name}:placed_jukebox
execute as @s run function {datapack_name}:raycast_start
"""
}

play = {
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', 'play.mcfunction'],
    'repeat': 'copy_within', #single, copy_within, copy
    'contents': \
"""
execute if score @e[type=marker,tag=imd_jukebox_marker,distance=..0.1,limit=1] imd_disc_id matches {entry.custom_model_data} run function {datapack_name}:{entry.internal_name}/play
"""
}

play_duration = {
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', 'play_duration.mcfunction'],
    'repeat': 'copy_within',
    'contents': \
"""
execute if score @s imd_disc_id matches {entry.custom_model_data} run function {datapack_name}:{entry.internal_name}/play_duration
"""
}

pre_play = {
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', 'pre_play.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
execute store result score @s imd_disc_id run data get block ~ ~ ~ RecordItem.tag.CustomModelData
function {datapack_name}:play_duration
scoreboard players set @s imd_stop_11_time 2
function {datapack_name}:watchdog_reset_tickcount
execute as @a[distance=..64] run function {datapack_name}:register_jukebox_listener
"""
}

raycast_hit = {
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', 'raycast_hit.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
scoreboard players set @s imd_rc_steps 1
execute align xyz positioned ~0.5 ~0.5 ~0.5 unless entity @e[type=marker,tag=imd_jukebox_marker,distance=..0.1,limit=1] run function {datapack_name}:register_jukebox_marker
"""
}

raycast_start = {
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', 'raycast_start.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
scoreboard players set @s imd_rc_steps 1000
execute at @s anchored eyes positioned ^ ^ ^ run function {datapack_name}:raycast_step
"""
}

raycast_step = {
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', 'raycast_step.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
execute if block ~ ~ ~ minecraft:jukebox run function {datapack_name}:raycast_hit
scoreboard players remove @s imd_rc_steps 1
execute if score @s imd_rc_steps matches 1.. positioned ^ ^ ^0.005 run function {datapack_name}:raycast_step
"""
}

register_jukebox_listener = {
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', 'register_jukebox_listener.mcfunction'],
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
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', 'register_jukebox_marker.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
summon marker ~ ~ ~ {{Tags:["imd_jukebox_marker"]}}
"""
}

register_player = {
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', 'register_player.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
execute store result score @s imd_player_id run scoreboard players add #imd_id_global imd_player_id 1
tag @s[scores={{imd_player_id=1..}}] add imd_has_id
"""
}

register_players_tick = {
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', 'register_players_tick.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
execute as @a[tag=!imd_has_id] run function {datapack_name}:register_player
"""
}

#note that v2 generator doesn't use ReplaceItemCommand for pre-1.17 compatibility
#  since v2 datapack is not compatible with pre-1.19.4 versions anyway
set_disc_track = {
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', 'set_disc_track.mcfunction'],
    'repeat': 'copy_within',
    'contents': \
"""
execute as @s[nbt={{SelectedItem:{{id:"minecraft:music_disc_11", tag:{{CustomModelData:{entry.custom_model_data}}}}}}}] run item replace entity @s weapon.mainhand with minecraft:music_disc_11{{CustomModelData:{entry.custom_model_data}, HideFlags:32, display:{{Lore:["\\"\\\\u00a77{entry.title}\\""]}}}}
"""
}

setup_load = {
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', 'setup_load.mcfunction'],
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
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', 'stop.mcfunction'],
    'repeat': 'copy_within',
    'contents': \
"""
execute if score @s imd_disc_id matches {entry.custom_model_data} run function {datapack_name}:{entry.internal_name}/stop
"""
}

stop_11 = {
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', 'stop_11.mcfunction'],
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
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', 'watchdog_reset_tickcount.mcfunction'],
    'repeat': 'single',
    'contents': \
"""
execute as @e[type=marker,tag=imd_jukebox_marker,tag=imd_is_playing,tag=imd_has_custom_disc] at @s run data merge block ~ ~ ~ {{TickCount:0L}}
schedule function {datapack_name}:watchdog_reset_tickcount 10s replace
"""
}

# per-disc functions
disc_play = {
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', '{entry.internal_name}', 'play.mcfunction'],
    'repeat': 'copy',
    'contents': \
"""
title @s actionbar {{"text":"Now Playing: {entry.title}", "color":"green"}}
playsound minecraft:music_disc.{entry.internal_name} record @s ~ ~ ~ 4 1
"""
}

disc_play_duration = {
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', '{entry.internal_name}', 'play_duration.mcfunction'],
    'repeat': 'copy',
    'contents': \
"""
scoreboard players set @s imd_play_time {entry.length}
"""
}

disc_stop = {
    'path': ['{datapack_name}', 'data', '{datapack_name}', 'functions', '{entry.internal_name}', 'stop.mcfunction'],
    'repeat': 'copy',
    'contents': \
"""
execute store result score @s imd_player_id run data get entity @s data.Listeners[0]
data remove entity @s data.Listeners[0]
execute as @a if score @s imd_player_id = @e[type=marker,tag=imd_jukebox_marker,distance=..0.1,limit=1] imd_player_id run stopsound @s record minecraft:music_disc.{entry.internal_name}
execute if data entity @s data.Listeners[0] run function {datapack_name}:{entry.internal_name}/stop
"""
}

# iterable list of files
#TODO: possible to get rid of this so you can just add objects directly to this module?
file_list = [
    pack_mcmeta,
    creeper_json,
    placed_disc,
    placed_jukebox,
    load,
    tick,
    destroy_jukebox_marker,
    give_all_discs,
    give_disc,
    help,
    jukebox_check_playing,
    jukebox_event_tick,
    jukebox_on_play,
    jukebox_on_stop,
    jukebox_tick_timers,
    on_placed_disc,
    on_placed_jukebox,
    play,
    play_duration,
    pre_play,
    raycast_hit,
    raycast_start,
    raycast_step,
    register_jukebox_listener,
    register_jukebox_marker,
    register_player,
    register_players_tick,
    set_disc_track,
    setup_load,
    stop,
    stop_11,
    watchdog_reset_tickcount,
    disc_play,
    disc_play_duration,
    disc_stop
]


