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
        datapack_name_zip = datapack_name + Constants.ZIP_SUFFIX

        dp_version_str = ("v%d.%d" % (self._version_major, self._version_minor))

        #TODO: use 'with expr as var'
        #TODO: shorten lines if possible
        #TODO: pretty-print json files
        try:
            # generate basic framework files
            #build datapack directory tree
            shutil.rmtree(datapack_name, ignore_errors=True)
            os.makedirs(os.path.join(datapack_name, 'data', 'minecraft', 'tags', 'functions'))
            os.makedirs(os.path.join(datapack_name, 'data', 'minecraft', 'loot_tables', 'entities'))
            os.makedirs(os.path.join(datapack_name, 'data', datapack_name, 'functions'))
            os.makedirs(os.path.join(datapack_name, 'data', datapack_name, 'advancements'))

            #write 'pack.mcmeta'
            pack = open(os.path.join(datapack_name, 'pack.mcmeta'), 'w', encoding='utf-8')
            pack.write(json.dumps({'pack':{'pack_format':pack_format, 'description':(Constants.DATAPACK_DESC % len(internal_names))}}, indent=4))
            pack.close()

            #write 'load.json'
            load = open(os.path.join(datapack_name, 'data', 'minecraft', 'tags', 'functions', 'load.json'), 'w', encoding='utf-8')
            load.write(json.dumps({'values':['{}:setup_load'.format(datapack_name)]}, indent=4))
            load.close()

            #write 'tick.json'
            tick = open(os.path.join(datapack_name, 'data', 'minecraft', 'tags', 'functions', 'tick.json'), 'w', encoding='utf-8')
            tick.write(json.dumps({'values':['{}:register_players_tick'.format(datapack_name), '{}:jukebox_event_tick'.format(datapack_name)]}, indent=4))
            tick.close()


            # generate advancements and related 'jukebox register' functions
            #write 'placed_disc.json'
            placed_disc = open(os.path.join(datapack_name, 'data', datapack_name, 'advancements', 'placed_disc.json'), 'w', encoding='utf-8')
            placed_disc.write(json.dumps({"criteria": {"placed_music_disc": {"trigger": "minecraft:item_used_on_block","conditions": {"location": {"block": {"blocks": [ "minecraft:jukebox" ], "state": { "has_record":"true" }}}, "item": {"tag": "minecraft:music_discs"}}}}, "rewards": {"function": "{}:on_placed_disc".format(datapack_name)}}))
            placed_disc.close()

            #write 'placed_jukebox.json'
            placed_jukebox = open(os.path.join(datapack_name, 'data', datapack_name, 'advancements', 'placed_jukebox.json'), 'w', encoding='utf-8')
            placed_jukebox.write(json.dumps({"criteria": {"placed_jukebox": {"trigger": "minecraft:placed_block", "conditions": {"block": "minecraft:jukebox", "item": {"items": [ "minecraft:jukebox" ]}}}}, "rewards": {"function": "{}:on_placed_jukebox".format(datapack_name)}}))
            placed_jukebox.close()

            #write 'on_placed_disc.mcfunction'
            on_placed_disc = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'on_placed_disc.mcfunction'), 'w', encoding='utf-8')
            on_placed_disc.writelines(['advancement revoke @s only %s:placed_disc\n' % (datapack_name),
                                       'execute as @s run function %s:raycast_start\n' % (datapack_name)])
            on_placed_disc.close()

            #write 'on_placed_jukebox.mcfunction'
            on_placed_jukebox = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'on_placed_jukebox.mcfunction'), 'w', encoding='utf-8')
            on_placed_jukebox.writelines(['advancement revoke @s only %s:placed_jukebox\n' % (datapack_name),
                                          'execute as @s run function %s:raycast_start\n' % (datapack_name)])
            on_placed_jukebox.close()

            #write 'raycast_start.mcfunction'
            rc_start = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'raycast_start.mcfunction'), 'w', encoding='utf-8')
            rc_start.writelines(['scoreboard players set @s imd_rc_steps 1000\n',
                                 'execute at @s anchored eyes positioned ^ ^ ^ run function %s:raycast_step\n' % (datapack_name)])
            rc_start.close()

            #write 'raycast_step.mcfunction'
            rc_step = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'raycast_step.mcfunction'), 'w', encoding='utf-8')
            rc_step.writelines(['execute if block ~ ~ ~ minecraft:jukebox run function %s:raycast_hit\n' % (datapack_name),
                                'scoreboard players remove @s imd_rc_steps 1\n',
                                'execute if score @s imd_rc_steps matches 1.. positioned ^ ^ ^0.005 run function %s:raycast_step\n' % (datapack_name)])
            rc_step.close()

            #write 'raycast_hit.mcfunction'
            rc_hit = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'raycast_hit.mcfunction'), 'w', encoding='utf-8')
            rc_hit.writelines(['scoreboard players set @s imd_rc_steps 1\n',
                               'execute align xyz positioned ~0.5 ~0.5 ~0.5 unless entity @e[type=marker,tag=imd_jukebox_marker,distance=..0.1,limit=1] run function %s:register_jukebox_marker\n' % (datapack_name)])
            rc_hit.close()

            #write 'register_jukebox_marker.mcfunction'
            reg_jukebox_marker = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'register_jukebox_marker.mcfunction'), 'w', encoding='utf-8')
            reg_jukebox_marker.write('summon marker ~ ~ ~ {Tags:["imd_jukebox_marker"]}\n')
            reg_jukebox_marker.close()


            # write jukebox related every-tick functions
            #write 'jukebox_event_tick.mcfunction'
            jb_event_tick = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'jukebox_event_tick.mcfunction'), 'w', encoding='utf-8')
            jb_event_tick.writelines(['execute as @e[type=marker,tag=imd_jukebox_marker] at @s unless block ~ ~ ~ minecraft:jukebox run function %s:destroy_jukebox_marker\n' % (datapack_name),
                                      'execute as @e[type=marker,tag=imd_jukebox_marker] at @s if block ~ ~ ~ minecraft:jukebox run function %s:jukebox_check_playing\n' % (datapack_name),
                                      'execute as @e[type=marker,tag=imd_jukebox_marker,tag=imd_is_playing,tag=imd_has_custom_disc] at @s run function %s:jukebox_tick_timers\n' % (datapack_name)])
            jb_event_tick.close()

            #FIXME: only stop if jukebox is currently playing
            #write 'destroy_jukebox_marker.mcfunction'
            #TBD

            #write 'jukebox_tick_timers.mcfunction'
            jb_tick_timers = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'jukebox_tick_timers.mcfunction'), 'w', encoding='utf-8')
            jb_tick_timers.writelines(['execute as @s[scores={imd_play_time=1..}] run scoreboard players remove @s imd_play_time 1\n',
                                       'execute as @s[scores={imd_stop_11_time=1..}] run scoreboard players remove @s imd_stop_11_time 1\n',
                                       'execute as @s[scores={imd_play_time=0}] run data merge block ~ ~ ~ {RecordStartTick:-999999L}\n',
                                       'execute as @s[scores={imd_stop_11_time=0},tag=!imd_stopped_11] run function %s:stop_11\n' % (datapack_name)])
            jb_tick_timers.close()

            #write 'jukebox_check_playing.mcfunction'
            jb_check_playing = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'jukebox_check_playing.mcfunction'), 'w', encoding='utf-8')
            jb_check_playing.writelines(['execute as @s[tag=!imd_is_playing] if block ~ ~ ~ minecraft:jukebox{IsPlaying:1b} run function %s:jukebox_on_play\n' % (datapack_name),
                                         'execute as @s[tag=imd_is_playing] unless block ~ ~ ~ minecraft:jukebox{IsPlaying:1b} run function %s:jukebox_on_stop\n' % (datapack_name)])
            jb_check_playing.close()

            #TODO: technically should check if custommodeldata is within acceptable range
            #write 'jukebox_on_play.mcfunction'
            jb_on_play = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'jukebox_on_play.mcfunction'), 'w', encoding='utf-8')
            jb_on_play.writelines(['tag @s add imd_is_playing\n',
                                   'execute if data block ~ ~ ~ RecordItem.tag.CustomModelData run tag @s add imd_has_custom_disc\n',
                                   'execute as @s[tag=imd_has_custom_disc] run function %s:pre_play\n' % (datapack_name)])
            jb_on_play.close()

            #write 'pre_play.mcfunction'
            pre_play = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'pre_play.mcfunction'), 'w', encoding='utf-8')
            pre_play.writelines(['execute store result score @s imd_disc_id run data get block ~ ~ ~ RecordItem.tag.CustomModelData\n',
                                 'function %s:play_duration\n' % (datapack_name),
                                 'scoreboard players set @s imd_stop_11_time 2\n',
                                 'function %s:watchdog_reset_tickcount\n' % (datapack_name),
                                 'execute as @a[distance=..64] run function %s:register_jukebox_listener\n' % (datapack_name)])
            pre_play.close()

            #write 'register_jukebox_listener.mcfunction'
            #TODO: 2 lists is sloppy, try to optimize
            reg_jukebox_listener = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'register_jukebox_listener.mcfunction'), 'w', encoding='utf-8')
            reg_jukebox_listener.writelines(['execute store result storage %s:global tmp.Player int 1.0 run scoreboard players get @s imd_player_id\n' % (datapack_name),
                                             'data modify entity @e[type=marker,tag=imd_jukebox_marker,distance=..0.1,limit=1] data.Listeners append from storage %s:global tmp.Player\n' % (datapack_name),
                                             'data modify entity @e[type=marker,tag=imd_jukebox_marker,distance=..0.1,limit=1] data.Listeners_11 append from storage %s:global tmp.Player\n' % (datapack_name),
                                             'function %s:play\n' % (datapack_name)])
            reg_jukebox_listener.close()

            #write 'jukebox_on_stop.mcfunction'
            jb_on_stop = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'jukebox_on_stop.mcfunction'), 'w', encoding='utf-8')
            jb_on_stop.writelines(['tag @s remove imd_is_playing\n',
                                   'tag @s remove imd_has_custom_disc\n',
                                   'tag @s remove imd_stopped_11\n',
                                   'function %s:stop\n' % (datapack_name)])
            jb_on_stop.close()




#-
            #write 'setup_load.mcfunction'
            setup_load = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'setup_load.mcfunction'), 'w', encoding='utf-8')
            setup_load.writelines(['scoreboard objectives add usedDisc minecraft.used:minecraft.music_disc_11\n',
                                'scoreboard objectives add heldDisc dummy\n',
                                '\n',
                                'tellraw @a {"text":"Infinite Music Discs %s by link2_thepast","color":"yellow"}\n' % (dp_version_str)])
            setup_load.close()

            #write 'detect_play_tick.mcfunction'
            detect_play_tick = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'detect_play_tick.mcfunction'), 'w', encoding='utf-8')
            detect_play_tick.writelines(['execute as @a[scores={usedDisc=0}] run scoreboard players set @s heldDisc -1\n',
                                        'execute as @a[scores={usedDisc=0},nbt={Inventory:[{Slot:-106b,id:"minecraft:music_disc_11"}]}] store result score @s heldDisc run data get entity @s Inventory[{Slot:-106b}].tag.CustomModelData\n',
                                        'execute as @a[scores={usedDisc=0},nbt={SelectedItem:{id:"minecraft:music_disc_11"}}] store result score @s heldDisc run data get entity @s SelectedItem.tag.CustomModelData\n',
                                        'execute as @a[scores={usedDisc=2}] run function %s:disc_play\n' % (datapack_name),
                                        '\n',
                                        'execute as @a run scoreboard players add @s usedDisc 0\n',
                                        'execute as @a[scores={usedDisc=2..}] run scoreboard players set @s usedDisc 0\n',
                                        'scoreboard players add @a[scores={usedDisc=1}] usedDisc 1\n'])
            detect_play_tick.close()

            #write 'disc_play.mcfunction'
            disc_play = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'disc_play.mcfunction'), 'w', encoding='utf-8')

            for i, name in enumerate(internal_names):
                j = i + offset + 1

                disc_play.write('execute as @s[scores={heldDisc=%d}] run function %s:play_%s\n' % (j, datapack_name, name))

            disc_play.close()

            #write 'detect_stop_tick.mcfunction'
            detect_stop_tick = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'detect_stop_tick.mcfunction'), 'w', encoding='utf-8')

            detect_stop_tick.writelines(['execute as @e[type=item, nbt={Item:{id:"minecraft:music_disc_11"}}] at @s unless entity @s[tag=old] if block ~ ~-1 ~ minecraft:jukebox run function %s:disc_stop\n' % (datapack_name),
                                        'execute as @e[type=item, nbt={Item:{id:"minecraft:music_disc_11"}}] at @s unless entity @s[tag=old] if block ~ ~ ~ minecraft:jukebox run function %s:disc_stop\n' % (datapack_name),
                                        'execute as @e[type=item, nbt={Item:{id:"minecraft:music_disc_11"}}] at @s unless entity @s[tag=old] run tag @s add old\n'])
            detect_stop_tick.close()

            #write 'disc_stop.mcfunction'
            disc_stop = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'disc_stop.mcfunction'), 'w', encoding='utf-8')

            for i, name in enumerate(internal_names):
                j = i + offset + 1

                disc_stop.write('execute as @s[nbt={Item:{tag:{CustomModelData:%d}}}] at @s run stopsound @a[distance=..64] record minecraft:music_disc.%s\n' % (j, name))

            disc_stop.close()

            #write 'set_disc_track.mcfunction'
            set_disc_track = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'set_disc_track.mcfunction'), 'w', encoding='utf-8')

            for i, track in enumerate(titles):
                j = i + offset + 1

                # Create command, and add command as string to the rest of the command.
                item_cmd = ReplaceItemCommand(target_entity="@s", slot=ItemSlot.WEAPON_MAINHAND, item="minecraft:music_disc_11{CustomModelData:%d, HideFlags:32, display:{Lore:[\"\\\"\\\\u00a77%s\\\"\"]}}")
                cmd_str = 'execute as @s[nbt={SelectedItem:{id:"minecraft:music_disc_11", tag:{CustomModelData:%d}}}] run ' + item_cmd.command_by_pack_format(pack_format) + '\n'

                set_disc_track.write(cmd_str % (j, j, track.replace('"', '')))

            set_disc_track.close()

            #write 'play_*.mcfunction' files
            for i, name in enumerate(internal_names):
                play = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'play_%s.mcfunction' % name), 'w', encoding='utf-8')
                play.writelines(['execute as @s at @s run title @a[distance=..64] actionbar {"text":"Now Playing: %s","color":"green"}\n' % (titles[i].replace('"', '')),
                                'execute as @s at @s run stopsound @a[distance=..64] record minecraft:music_disc.11\n',
                                'execute as @s at @s run playsound minecraft:music_disc.%s record @a[distance=..64] ~ ~ ~ 4 1\n' % name])
                play.close()

            #write 'give_*_disc.mcfunction' files
            for i, track in enumerate(titles):
                j = i + offset + 1

                give = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'give_%s.mcfunction' % internal_names[i]), 'w', encoding='utf-8')
                give.write('execute as @s at @s run summon item ~ ~ ~ {Item:{id:"minecraft:music_disc_11", Count:1b, tag:{CustomModelData:%d, HideFlags:32, display:{Lore:[\"\\\"\\\\u00a77%s\\\"\"]}}}}\n' % (j, track))
                give.close()

            #write 'give_all_discs.mcfunction'
            give_all = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'give_all_discs.mcfunction'), 'w', encoding='utf-8')

            for i, track in enumerate(titles):
                j = i + offset + 1

                give_all.write('execute as @s at @s run summon item ~ ~ ~ {Item:{id:"minecraft:music_disc_11", Count:1b, tag:{CustomModelData:%d, HideFlags:32, display:{Lore:[\"\\\"\\\\u00a77%s\\\"\"]}}}}\n' % (j, track))

            give_all.close()

            #write 'creeper.json'
            creeper = open(os.path.join(datapack_name, 'data', 'minecraft', 'loot_tables', 'entities', 'creeper.json'), 'w', encoding='utf-8')

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
            creeper.close()


        except UnicodeEncodeError as e:
            return Status.BAD_UNICODE_CHAR

        #copy pack.png
        try:
            if 'pack' in user_settings:
                shutil.copyfile(user_settings['pack'], os.path.join(datapack_name, 'pack.png'))
            else:
                raise FileNotFoundError

        except (FileNotFoundError, IOError) as e:
            print("Warning: No pack.png found. Your datapack will not have an icon.")

        #move pack to .zip, if selected
        try:
            if 'zip' in user_settings and user_settings['zip']:
                #remove old zip
                if os.path.exists(datapack_name_zip):
                    os.remove(datapack_name_zip)

                #generate new zip archive
                with zipfile.ZipFile(datapack_name_zip, 'w') as dp_zip:
                    for root, dirs, files in os.walk(datapack_name):
                        root_zip = os.path.relpath(root, datapack_name)

                        for file in files:
                            dp_zip.write(os.path.join(root, file), os.path.join(root_zip, file))

                #remove datapack folder
                if os.path.exists(datapack_name_zip):
                    shutil.rmtree(datapack_name, ignore_errors=True)

        except (OSError, zipfile.BadZipFile) as e:
            #remove bad zip, if it exists
            if os.path.exists(datapack_name_zip):
                os.remove(datapack_name_zip)

            print("Error: Failed to zip datapack. Datapack has been generated as folder instead.")
            return Status.BAD_ZIP

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
        resourcepack_name_zip = resourcepack_name + Constants.ZIP_SUFFIX

        try:
            #build resourcepack directory tree
            shutil.rmtree(resourcepack_name, ignore_errors=True)
            os.makedirs(os.path.join(resourcepack_name, 'assets', 'minecraft', 'models', 'item'))
            os.makedirs(os.path.join(resourcepack_name, 'assets', 'minecraft', 'sounds', 'records'))
            os.makedirs(os.path.join(resourcepack_name, 'assets', 'minecraft', 'textures', 'item'))

            #write 'pack.mcmeta'
            pack = open(os.path.join(resourcepack_name, 'pack.mcmeta'), 'w', encoding='utf-8')
            pack.write(json.dumps({'pack':{'pack_format':pack_format, 'description':(Constants.RESOURCEPACK_DESC % len(internal_names))}}, indent=4))
            pack.close()

            #write 'sounds.json'
            pack = open(os.path.join(resourcepack_name, 'assets', 'minecraft', 'sounds.json'), 'w', encoding='utf-8')
            pack.write('{')

            for i, name in enumerate(internal_names):
                pack.write('\n"music_disc.{}": '.format(name))
                pack.write(json.dumps({'sounds': [{'name': 'records/{}'.format(name), 'stream':True}]}, indent=4))

                if i < len(internal_names)-1:
                    pack.write(',\n')

            pack.write('\n}')
            pack.close()

            #write 'music_disc_11.json'
            music_disc_11 = open(os.path.join(resourcepack_name, 'assets', 'minecraft', 'models', 'item', 'music_disc_11.json'), 'w', encoding='utf-8')

            json_list = []
            for i, name in enumerate(internal_names):
                j = i + offset + 1

                json_list.append({'predicate': {'custom_model_data':j}, 'model': 'item/music_disc_{}'.format(name)})

            music_disc_11.write(json.dumps({'parent': 'item/generated', 'textures': {'layer0': 'item/music_disc_11'}, 'overrides': json_list}, indent=4))
            music_disc_11.close()

            #write 'music_disc_*.json' files
            for name in internal_names:
                music_disc = open(os.path.join(resourcepack_name, 'assets', 'minecraft', 'models', 'item', 'music_disc_%s.json' % name), 'w', encoding='utf-8')
                music_disc.write(json.dumps({'parent': 'item/generated', 'textures': {'layer0': 'item/music_disc_{}'.format(name)}}, indent=4))
                music_disc.close()

            #copy sound and texture files
            for i, name in enumerate(internal_names):
                shutil.copyfile(track_files[i], os.path.join(resourcepack_name, 'assets', 'minecraft', 'sounds', 'records', '%s.ogg' % name))
                shutil.copyfile(texture_files[i], os.path.join(resourcepack_name, 'assets', 'minecraft', 'textures', 'item', 'music_disc_%s.png' % name))

        except UnicodeEncodeError:
            return Status.BAD_UNICODE_CHAR

        #copy pack.png
        try:
            if 'pack' in user_settings:
                shutil.copyfile(user_settings['pack'], os.path.join(resourcepack_name, 'pack.png'))
            else:
                raise FileNotFoundError

        except (FileNotFoundError, IOError) as e:
            print("Warning: No pack.png found. Your resourcepack will not have an icon.")

        #move pack to .zip, if selected
        try:
            if 'zip' in user_settings and user_settings['zip']:
                #remove old zip
                if os.path.exists(resourcepack_name_zip):
                    os.remove(resourcepack_name_zip)

                #generate new zip archive
                with zipfile.ZipFile(resourcepack_name_zip, 'w') as rp_zip:
                    for root, dirs, files in os.walk(resourcepack_name):
                        root_zip = os.path.relpath(root, resourcepack_name)

                        for file in files:
                            rp_zip.write(os.path.join(root, file), os.path.join(root_zip, file))

                #remove resourcepack folder
                if os.path.exists(resourcepack_name_zip):
                    shutil.rmtree(resourcepack_name, ignore_errors=True)

        except (OSError, zipfile.BadZipFile) as e:
            #remove bad zip, if it exists
            if os.path.exists(resourcepack_name_zip):
                os.remove(resourcepack_name_zip)

            print("Error: Failed to zip resourcepack. Resourcepack has been generated as folder instead.")
            return Status.BAD_ZIP

        #cleanup temp work directory
        if cleanup_tmp:
            shutil.rmtree(self.tmp_path, ignore_errors=True)
            self.tmp_path = None

        return Status.SUCCESS


