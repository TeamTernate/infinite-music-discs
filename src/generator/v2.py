#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#Infinite Music Discs generator module implementation
#Generation tool, datapack design, and resourcepack design by link2_thepast
#
#Generates datapack v2.0

import os
import json
import shutil
import zipfile

from src.definitions import Constants, Status, DiscListContents
from src.commands import ReplaceItemCommand, ItemSlot

from src.generator.base import VirtualGenerator



class GeneratorV2(VirtualGenerator):

    #TODO: break into smaller functions so it's easier to understand behavior?
    #TODO: break by section into smaller functions
    def generate_datapack(self, entry_list: DiscListContents, user_settings={}):
        titles = entry_list.titles
        internal_names = entry_list.internal_names

        #read settings
        pack_format = user_settings.get('version').get('dp', Constants.DEFAULT_PACK_FORMAT)
        offset = user_settings.get('offset', 0)

        datapack_name = user_settings.get('name', Constants.DEFAULT_PACK_NAME)
        datapack_name = datapack_name + Constants.DATAPACK_SUFFIX

        dp_version_str = ("v%d.%d" % (self._version_major, self._version_minor))

        #TODO: shorten lines if possible
        #TODO: pretty-print json files
        #TODO: move pwd inside datapack as you go, cut down on os path join length
        try:
            # generate basic framework files
            #build datapack directory tree
            shutil.rmtree(datapack_name, ignore_errors=True)
            os.makedirs(os.path.join(datapack_name, 'data', 'minecraft', 'tags', 'functions'))
            os.makedirs(os.path.join(datapack_name, 'data', 'minecraft', 'loot_tables', 'entities'))
            os.makedirs(os.path.join(datapack_name, 'data', datapack_name, 'functions'))
            os.makedirs(os.path.join(datapack_name, 'data', datapack_name, 'advancements'))

            #write 'pack.mcmeta'
            with open(os.path.join(datapack_name, 'pack.mcmeta'), 'w', encoding='utf-8') as pack:
                pack.write(json.dumps({
                    'pack': {
                        'pack_format': pack_format,
                        'description': (Constants.DATAPACK_DESC % len(internal_names))
                    }
                }, indent=4))

            #write 'load.json'
            with open(os.path.join(datapack_name, 'data', 'minecraft', 'tags', 'functions', 'load.json'), 'w', encoding='utf-8') as load:
                load.write(json.dumps({
                    'values': [ f'{datapack_name}:setup_load' ]
                }, indent=4))

            #write 'tick.json'
            with open(os.path.join(datapack_name, 'data', 'minecraft', 'tags', 'functions', 'tick.json'), 'w', encoding='utf-8') as tick:
                tick.write(json.dumps({
                    'values': [
                        f'{datapack_name}:register_players_tick',
                        f'{datapack_name}:jukebox_event_tick'
                    ]
                }, indent=4))

            #write 'setup_load.mcfunction'
            with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'setup_load.mcfunction'), 'w', encoding='utf-8') as setup_load:
                setup_load.writelines([
                    'scoreboard objectives add imd_player_id dummy\n',
                    'scoreboard objectives add imd_disc_id dummy\n',
                    'scoreboard objectives add imd_rc_steps dummy\n',
                    'scoreboard objectives add imd_play_time dummy\n',
                    'scoreboard objectives add imd_stop_11_time dummy\n',
                    '\n',
                    f'advancement revoke @a only {datapack_name}:placed_disc\n',
                    f'advancement revoke @a only {datapack_name}:placed_jukebox\n',
                    f'tellraw @a {{"text":"Infinite Music Discs {dp_version_str} by link2_thepast","color":"gold"}}\n'
                ])

            #write 'watchdog_reset_tickcount.mcfunction'
            with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'watchdog_reset_tickcount.mcfunction'), 'w', encoding='utf-8') as wd_reset_tickcount:
                wd_reset_tickcount.writelines([
                    'execute as @e[type=marker,tag=imd_jukebox_marker,tag=imd_is_playing,tag=imd_has_custom_disc] at @s run data merge block ~ ~ ~ {TickCount:0L}\n',
                    f'schedule function {datapack_name}:watchdog_reset_tickcount 10s replace\n'
                ])


            # generate advancements and related 'jukebox register' functions
            #write 'placed_disc.json'
            with open(os.path.join(datapack_name, 'data', datapack_name, 'advancements', 'placed_disc.json'), 'w', encoding='utf-8') as placed_disc:
                placed_disc.write(json.dumps({
                    'criteria': {
                        'placed_music_disc': {
                            'trigger': 'minecraft:item_used_on_block',
                            'conditions': {
                                'location': {
                                    'block': {
                                        'blocks': [ 'minecraft:jukebox' ],
                                        'state': { 'has_record':'true' }
                                    }
                                },
                                'item': {'tag': 'minecraft:music_discs'}
                            }
                        }
                    },
                    'rewards': {
                        'function': f'{datapack_name}:on_placed_disc'
                    }
                }, indent=4))

            #write 'placed_jukebox.json'
            with open(os.path.join(datapack_name, 'data', datapack_name, 'advancements', 'placed_jukebox.json'), 'w', encoding='utf-8') as placed_jukebox:
                placed_jukebox.write(json.dumps({
                    'criteria': {
                        'placed_jukebox': {
                            'trigger': 'minecraft:placed_block',
                            'conditions': {
                                'block': 'minecraft:jukebox',
                                'item': {
                                    'items': [ 'minecraft:jukebox' ]
                                }
                            }
                        }
                    },
                    'rewards': {
                        'function': f'{datapack_name}:on_placed_jukebox'
                    }
                }, indent=4))

            #write 'on_placed_disc.mcfunction'
            with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'on_placed_disc.mcfunction'), 'w', encoding='utf-8') as on_placed_disc:
                on_placed_disc.writelines(['advancement revoke @s only %s:placed_disc\n' % (datapack_name),
                                           'execute as @s run function %s:raycast_start\n' % (datapack_name)])

            #write 'on_placed_jukebox.mcfunction'
            with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'on_placed_jukebox.mcfunction'), 'w', encoding='utf-8') as on_placed_jukebox:
                on_placed_jukebox.writelines(['advancement revoke @s only %s:placed_jukebox\n' % (datapack_name),
                                              'execute as @s run function %s:raycast_start\n' % (datapack_name)])

            #write 'raycast_start.mcfunction'
            with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'raycast_start.mcfunction'), 'w', encoding='utf-8') as rc_start:
                rc_start.writelines(['scoreboard players set @s imd_rc_steps 1000\n',
                                     'execute at @s anchored eyes positioned ^ ^ ^ run function %s:raycast_step\n' % (datapack_name)])

            #write 'raycast_step.mcfunction'
            with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'raycast_step.mcfunction'), 'w', encoding='utf-8') as rc_step:
                rc_step.writelines(['execute if block ~ ~ ~ minecraft:jukebox run function %s:raycast_hit\n' % (datapack_name),
                                    'scoreboard players remove @s imd_rc_steps 1\n',
                                    'execute if score @s imd_rc_steps matches 1.. positioned ^ ^ ^0.005 run function %s:raycast_step\n' % (datapack_name)])

            #write 'raycast_hit.mcfunction'
            with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'raycast_hit.mcfunction'), 'w', encoding='utf-8') as rc_hit:
                rc_hit.writelines(['scoreboard players set @s imd_rc_steps 1\n',
                                   'execute align xyz positioned ~0.5 ~0.5 ~0.5 unless entity @e[type=marker,tag=imd_jukebox_marker,distance=..0.1,limit=1] run function %s:register_jukebox_marker\n' % (datapack_name)])

            #write 'register_jukebox_marker.mcfunction'
            with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'register_jukebox_marker.mcfunction'), 'w', encoding='utf-8') as reg_jukebox_marker:
                reg_jukebox_marker.write('summon marker ~ ~ ~ {Tags:["imd_jukebox_marker"]}\n')


            # generate jukebox related every-tick functions
            #write 'jukebox_event_tick.mcfunction'
            with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'jukebox_event_tick.mcfunction'), 'w', encoding='utf-8') as jb_event_tick:
                jb_event_tick.writelines(['execute as @e[type=marker,tag=imd_jukebox_marker] at @s unless block ~ ~ ~ minecraft:jukebox run function %s:destroy_jukebox_marker\n' % (datapack_name),
                                          'execute as @e[type=marker,tag=imd_jukebox_marker] at @s if block ~ ~ ~ minecraft:jukebox run function %s:jukebox_check_playing\n' % (datapack_name),
                                          'execute as @e[type=marker,tag=imd_jukebox_marker,tag=imd_is_playing,tag=imd_has_custom_disc] at @s run function %s:jukebox_tick_timers\n' % (datapack_name)])

            #FIXME: only stop if jukebox is currently playing
            #write 'destroy_jukebox_marker.mcfunction'
            with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'destroy_jukebox_marker.mcfunction'), 'w', encoding='utf-8') as destroy_jb_marker:
                destroy_jb_marker.writelines(['function %s:stop\n' % (datapack_name),
                                              'kill @s\n'])

            #write 'jukebox_tick_timers.mcfunction'
            with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'jukebox_tick_timers.mcfunction'), 'w', encoding='utf-8') as jb_tick_timers:
                jb_tick_timers.writelines(['execute as @s[scores={imd_play_time=1..}] run scoreboard players remove @s imd_play_time 1\n',
                                           'execute as @s[scores={imd_stop_11_time=1..}] run scoreboard players remove @s imd_stop_11_time 1\n',
                                           'execute as @s[scores={imd_play_time=0}] run data merge block ~ ~ ~ {RecordStartTick:-999999L}\n',
                                           'execute as @s[scores={imd_stop_11_time=0},tag=!imd_stopped_11] run function %s:stop_11\n' % (datapack_name)])

            #TODO: in multiplayer is marker tagged multiple times, once per player?
            #write 'stop_11.mcfunction'
            with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'stop_11.mcfunction'), 'w', encoding='utf-8') as stop_11:
                stop_11.writelines(['execute store result score @s imd_player_id run data get entity @s data.Listeners_11[0]\n',
                                    'data remove entity @s data.Listeners_11[0]\n',
                                    'execute as @a if score @s imd_player_id = @e[type=marker,tag=imd_jukebox_marker,distance=..0.1,limit=1] imd_player_id run stopsound @s record minecraft:music_disc.11\n',
                                    'execute if data entity @s data.Listeners_11[0] run function %s:stop_11\n' % (datapack_name),
                                    'execute unless data entity @s data.Listeners_11[0] run tag @s add imd_stopped_11\n'])

            #write 'jukebox_check_playing.mcfunction'
            with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'jukebox_check_playing.mcfunction'), 'w', encoding='utf-8') as jb_check_playing:
                jb_check_playing.writelines(['execute as @s[tag=!imd_is_playing] if block ~ ~ ~ minecraft:jukebox{IsPlaying:1b} run function %s:jukebox_on_play\n' % (datapack_name),
                                             'execute as @s[tag=imd_is_playing] unless block ~ ~ ~ minecraft:jukebox{IsPlaying:1b} run function %s:jukebox_on_stop\n' % (datapack_name)])

            #TODO: technically should check if custommodeldata is within acceptable range
            #write 'jukebox_on_play.mcfunction'
            with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'jukebox_on_play.mcfunction'), 'w', encoding='utf-8') as jb_on_play:
                jb_on_play.writelines(['tag @s add imd_is_playing\n',
                                       'execute if data block ~ ~ ~ RecordItem.tag.CustomModelData run tag @s add imd_has_custom_disc\n',
                                       'execute as @s[tag=imd_has_custom_disc] run function %s:pre_play\n' % (datapack_name)])

            #write 'pre_play.mcfunction'
            with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'pre_play.mcfunction'), 'w', encoding='utf-8') as pre_play:
                pre_play.writelines(['execute store result score @s imd_disc_id run data get block ~ ~ ~ RecordItem.tag.CustomModelData\n',
                                     'function %s:play_duration\n' % (datapack_name),
                                     'scoreboard players set @s imd_stop_11_time 2\n',
                                     'function %s:watchdog_reset_tickcount\n' % (datapack_name),
                                     'execute as @a[distance=..64] run function %s:register_jukebox_listener\n' % (datapack_name)])

            #write 'register_jukebox_listener.mcfunction'
            #TODO: 2 lists is sloppy, try to optimize
            with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'register_jukebox_listener.mcfunction'), 'w', encoding='utf-8') as reg_jukebox_listener:
                reg_jukebox_listener.writelines(['execute store result storage %s:global tmp.Player int 1.0 run scoreboard players get @s imd_player_id\n' % (datapack_name),
                                                 'data modify entity @e[type=marker,tag=imd_jukebox_marker,distance=..0.1,limit=1] data.Listeners append from storage %s:global tmp.Player\n' % (datapack_name),
                                                 'data modify entity @e[type=marker,tag=imd_jukebox_marker,distance=..0.1,limit=1] data.Listeners_11 append from storage %s:global tmp.Player\n' % (datapack_name),
                                                 'function %s:play\n' % (datapack_name)])

            #write 'jukebox_on_stop.mcfunction'
            with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'jukebox_on_stop.mcfunction'), 'w', encoding='utf-8') as jb_on_stop:
                jb_on_stop.writelines(['tag @s remove imd_is_playing\n',
                                       'tag @s remove imd_has_custom_disc\n',
                                       'tag @s remove imd_stopped_11\n',
                                       'function %s:stop\n' % (datapack_name)])


            # generate player related every-tick functions
            #write 'register_players_tick.mcfunction'
            with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'register_players_tick.mcfunction'), 'w', encoding='utf-8') as reg_players_tick:
                reg_players_tick.write('execute as @a[tag=!imd_has_id] run function %s:register_player\n' % (datapack_name))

            #TODO: different global id per-datapack?
            #write 'register_player.mcfunction'
            with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'register_player.mcfunction'), 'w', encoding='utf-8') as reg_player:
                reg_player.writelines(['execute store result score @s imd_player_id run scoreboard players add #imd_id_global imd_player_id 1\n',
                                       'tag @s[scores={imd_player_id=1..}] add imd_has_id'])


            # generate files with lines for every disc
            #write 'play.mcfunction'
            with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'play.mcfunction'), 'w', encoding='utf-8') as play:
                for i, name in enumerate(internal_names):
                    j = i + offset + 1

                    play.write('execute if score @e[type=marker,tag=imd_jukebox_marker,distance=..0.1,limit=1] imd_disc_id matches %d run function %s:%s/play\n' % (j, datapack_name, name))

            #write 'play_duration.mcfunction'
            with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'play_duration.mcfunction'), 'w', encoding='utf-8') as play_duration:
                for i, name in enumerate(internal_names):
                    j = i + offset + 1

                    play_duration.write('execute if score @s imd_disc_id matches %d run function %s:%s/play_duration\n' % (j, datapack_name, name))

            #write 'stop.mcfunction'
            with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'stop.mcfunction'), 'w', encoding='utf-8') as stop:
                for i, name in enumerate(internal_names):
                    j = i + offset + 1

                    stop.write('execute if score @s imd_disc_id matches %d run function %s:%s/stop\n' % (j, datapack_name, name))

            #write 'set_disc_track.mcfunction'
            with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'set_disc_track.mcfunction'), 'w', encoding='utf-8') as set_disc_track:
                for i, track in enumerate(titles):
                    j = i + offset + 1

                    # Create command, and add command as string to the rest of the command.
                    item_cmd = ReplaceItemCommand(target_entity="@s", slot=ItemSlot.WEAPON_MAINHAND, item="minecraft:music_disc_11{CustomModelData:%d, HideFlags:32, display:{Lore:[\"\\\"\\\\u00a77%s\\\"\"]}}")
                    cmd_str = 'execute as @s[nbt={SelectedItem:{id:"minecraft:music_disc_11", tag:{CustomModelData:%d}}}] run ' + item_cmd.command_by_pack_format(pack_format) + '\n'

                    set_disc_track.write(cmd_str % (j, j, track.replace('"', '')))

            #write 'give_all_discs.mcfunction'
            with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'give_all_discs.mcfunction'), 'w', encoding='utf-8') as give_all:
                for i, name in enumerate(internal_names):
                    j = i + offset + 1

                    give_all.write('execute at @s run function %s:give_%s\n' % (datapack_name, name))

            #write 'creeper.json'
            with open(os.path.join(datapack_name, 'data', 'minecraft', 'loot_tables', 'entities', 'creeper.json'), 'w', encoding='utf-8') as creeper:

                discs_tag = 'minecraft:creeper_drop_music_discs'
                if pack_format < 6:
                    discs_tag = 'minecraft:music_discs'

                creeper_mdentries = []
                creeper_mdentries.append({'type':'minecraft:tag', 'weight':1, 'name':discs_tag, 'expand':True})
                for i, track in enumerate(titles):
                    j = i + offset + 1

                    creeper_mdentries.append({'type':'minecraft:item', 'weight':1, 'name':'minecraft:music_disc_11', 'functions':[{'function':'minecraft:set_nbt', 'tag':'{CustomModelData:%d, HideFlags:32, display:{Lore:[\"\\\"\\\\u00a77%s\\\"\"]}}' % (j, track.replace('"', ''))}]})

                creeper_normentries = [{'type':'minecraft:item','functions':[{'function':'minecraft:set_count', 'count':{'min':0.0, 'max':2.0, 'type':'minecraft:uniform'}}, {'function':'minecraft:looting_enchant', 'count':{'min':0.0, 'max':1.0}}], 'name':'minecraft:gunpowder'}]
                creeper.write(json.dumps({'type':'minecraft:entity', 'pools':[{'rolls':1, 'entries':creeper_normentries}, {'rolls':1, 'entries':creeper_mdentries, 'conditions':[{'condition':'minecraft:entity_properties', 'predicate':{'type':'#minecraft:skeletons'}, 'entity':'killer'}]}]}, indent=4))


            # generate per-disc functions
            for i, entry in enumerate(entry_list.entries):
                #make directory for per-disc functions
                os.makedirs(os.path.join(datapack_name, 'data', datapack_name, 'functions', entry.internal_name))

                #write '*/play.mcfunction' files
                with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', entry.internal_name, 'play.mcfunction'), 'w', encoding='utf-8') as play:
                    play.writelines(['title @s actionbar {"text":"Now Playing: %s","color":"green"}\n' % (entry.title.replace('"', '')),
                                     'playsound minecraft:music_disc.%s record @s ~ ~ ~ 4 1\n' % entry.internal_name])

                #write '*/play_duration.mcfunction' files
                with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', entry.internal_name, 'play_duration.mcfunction'), 'w', encoding='utf-8') as play_duration:
                    play_duration.write('scoreboard players set @s imd_play_time %d\n' % (entry.length))

                #write '*/stop.mcfunction' files
                with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', entry.internal_name, 'stop.mcfunction'), 'w', encoding='utf-8') as stop:
                    stop.writelines(['execute store result score @s imd_player_id run data get entity @s data.Listeners[0]\n',
                                     'data remove entity @s data.Listeners[0]\n',
                                     'execute as @a if score @s imd_player_id = @e[type=marker,tag=imd_jukebox_marker,distance=..0.1,limit=1] imd_player_id run stopsound @s record minecraft:music_disc.%s\n' % (entry.internal_name),
                                     'execute if data entity @s data.Listeners[0] run function %s:%s/stop\n' % (datapack_name, entry.internal_name)])

                #write 'give_*_disc.mcfunction' files
                j = i + offset + 1

                with open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'give_%s.mcfunction' % entry.internal_name), 'w', encoding='utf-8') as give:
                    give.write('execute at @s run summon item ~ ~ ~ {Item:{id:"minecraft:music_disc_11", Count:1b, tag:{CustomModelData:%d, HideFlags:32, display:{Lore:[\"\\\"\\\\u00a77%s\\\"\"]}}}}\n' % (j, entry.title))


        except UnicodeEncodeError:
            return Status.BAD_UNICODE_CHAR

        #copy pack.png
        try:
            if 'pack' in user_settings:
                shutil.copyfile(user_settings['pack'], os.path.join(datapack_name, 'pack.png'))
            else:
                raise FileNotFoundError

        except (FileNotFoundError, IOError):
            print("Warning: No pack.png found. Your datapack will not have an icon.")

        #move pack to .zip, if selected
        if 'zip' in user_settings and user_settings['zip']:
            zip_status = self.zip_pack(datapack_name)

            if(zip_status != Status.SUCCESS):
                print("Error: Failed to zip datapack. Datapack has been generated as folder instead.")
                return zip_status

        return Status.SUCCESS



    def generate_resourcepack(self, entry_list: DiscListContents, user_settings={}, cleanup_tmp=True):
        texture_files = entry_list.texture_files
        track_files = entry_list.track_files
        internal_names = entry_list.internal_names

        #read settings
        pack_format = user_settings.get('version').get('rp', Constants.DEFAULT_PACK_FORMAT)
        offset = user_settings.get('offset', 0)

        resourcepack_name = user_settings.get('name', Constants.DEFAULT_PACK_NAME)
        resourcepack_name = resourcepack_name + Constants.RESOURCEPACK_SUFFIX

        try:
            #build resourcepack directory tree
            shutil.rmtree(resourcepack_name, ignore_errors=True)
            os.makedirs(os.path.join(resourcepack_name, 'assets', 'minecraft', 'models', 'item'))
            os.makedirs(os.path.join(resourcepack_name, 'assets', 'minecraft', 'sounds', 'records'))
            os.makedirs(os.path.join(resourcepack_name, 'assets', 'minecraft', 'textures', 'item'))

            #write 'pack.mcmeta'
            with open(os.path.join(resourcepack_name, 'pack.mcmeta'), 'w', encoding='utf-8') as pack:
                pack.write(json.dumps({'pack':{'pack_format':pack_format, 'description':(Constants.RESOURCEPACK_DESC % len(internal_names))}}, indent=4))

            #write 'sounds.json'
            with open(os.path.join(resourcepack_name, 'assets', 'minecraft', 'sounds.json'), 'w', encoding='utf-8') as sounds:
                sounds.write('{')

                for i, name in enumerate(internal_names):
                    sounds.write('\n"music_disc.{}": '.format(name))
                    sounds.write(json.dumps({'sounds': [{'name': 'records/{}'.format(name), 'stream':True}]}, indent=4))

                    if i < len(internal_names)-1:
                        sounds.write(',\n')

                sounds.write('\n}')

            #write 'music_disc_11.json'
            with open(os.path.join(resourcepack_name, 'assets', 'minecraft', 'models', 'item', 'music_disc_11.json'), 'w', encoding='utf-8') as music_disc_11:
                json_list = []
                for i, name in enumerate(internal_names):
                    j = i + offset + 1

                    json_list.append({'predicate': {'custom_model_data':j}, 'model': 'item/music_disc_{}'.format(name)})

                music_disc_11.write(json.dumps({'parent': 'item/generated', 'textures': {'layer0': 'item/music_disc_11'}, 'overrides': json_list}, indent=4))

            #write 'music_disc_*.json' files
            for name in internal_names:
                with open(os.path.join(resourcepack_name, 'assets', 'minecraft', 'models', 'item', 'music_disc_%s.json' % name), 'w', encoding='utf-8') as music_disc:
                    music_disc.write(json.dumps({'parent': 'item/generated', 'textures': {'layer0': 'item/music_disc_{}'.format(name)}}, indent=4))

            #copy sound and texture files
            for i, entry in enumerate(entry_list.entries):
                shutil.copyfile(entry.track_file, os.path.join(resourcepack_name, 'assets', 'minecraft', 'sounds', 'records', '%s.ogg' % entry.internal_name))
                shutil.copyfile(entry.texture_file, os.path.join(resourcepack_name, 'assets', 'minecraft', 'textures', 'item', 'music_disc_%s.png' % entry.internal_name))

        except UnicodeEncodeError:
            return Status.BAD_UNICODE_CHAR

        #copy pack.png
        try:
            if 'pack' in user_settings:
                shutil.copyfile(user_settings['pack'], os.path.join(resourcepack_name, 'pack.png'))
            else:
                raise FileNotFoundError

        except (FileNotFoundError, IOError):
            print("Warning: No pack.png found. Your resourcepack will not have an icon.")

        #move pack to .zip, if selected
        if 'zip' in user_settings and user_settings['zip']:
            zip_status = self.zip_pack(resourcepack_name)

            if(zip_status != Status.SUCCESS):
                print("Error: Failed to zip resourcepack. Resourcepack has been generated as folder instead.")
                return zip_status

        #cleanup temp work directory
        if cleanup_tmp:
            shutil.rmtree(self.tmp_path, ignore_errors=True)
            self.tmp_path = None

        return Status.SUCCESS



    def zip_pack(self, pack_name):
        pack_name_zip = pack_name + Constants.ZIP_SUFFIX

        try:
            #remove old zip
            if os.path.exists(pack_name_zip):
                os.remove(pack_name_zip)

            #generate new zip archive
            with zipfile.ZipFile(pack_name_zip, 'w') as rp_zip:
                for root, dirs, files in os.walk(pack_name):
                    root_zip = os.path.relpath(root, pack_name)

                    for file in files:
                        rp_zip.write(os.path.join(root, file), os.path.join(root_zip, file))

            #remove resourcepack folder
            if os.path.exists(pack_name_zip):
                shutil.rmtree(pack_name, ignore_errors=True)

        except (OSError, zipfile.BadZipFile):
            #remove bad zip, if it exists
            if os.path.exists(pack_name_zip):
                os.remove(pack_name_zip)

            return Status.BAD_ZIP
        
        return Status.SUCCESS


