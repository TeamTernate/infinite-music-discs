#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack + resourcepack generator module
#Generation tool, datapack design, and resourcepack design by link2_thepast
#
#Generates datapack v1.8

import os
import json
import shutil
import sys
import enum
import zipfile
import pyffmpeg

datapack_name = 'custom_music_discs_dp'
resourcepack_name = 'custom_music_discs_rp'

datapack_name_zip = datapack_name + '.zip'
resourcepack_name_zip = resourcepack_name + '.zip'

datapack_desc = 'Adds %d custom music discs'
resourcepack_desc = 'Adds %d custom music discs'

tmp_path = 'imd-tmp'    #TODO: use tempfile module
pack_format = 7


class Status(enum.Enum):
    SUCCESS = 0
    LIST_EMPTY = 1
    LIST_UNEVEN_LENGTH = 2
    IMAGE_FILE_MISSING = 3
    BAD_IMAGE_TYPE = 4
    TRACK_FILE_MISSING = 5
    BAD_TRACK_TYPE = 6
    BAD_INTERNAL_NAME = 7
    PACK_IMAGE_MISSING = 8
    BAD_PACK_IMAGE_TYPE = 9
    BAD_OGG_CONVERT = 10
    BAD_ZIP = 11



def validate(texture_files, track_files, titles, internal_names, packpng=''):
    #lists are all the same length
    if(not ( len(texture_files) == len(track_files) == len(titles) == len(internal_names) )):
        return Status.LIST_UNEVEN_LENGTH

    #lists are not empty
    if(len(texture_files) == 0):
        return Status.LIST_EMPTY

    for i in range(len(texture_files)):
        #image files still exist
        if(not os.path.isfile(texture_files[i])):
            return Status.IMAGE_FILE_MISSING

        #images are all .png
        if(not ( '.png' in texture_files[i] )):
            return Status.BAD_IMAGE_TYPE

        #track files still exist
        if(not os.path.isfile(track_files[i])):
            return Status.TRACK_FILE_MISSING

        #tracks are all .mp3, .wav, .ogg
        if(not ( '.mp3' in track_files[i] or '.wav' in track_files[i] or '.ogg' in track_files[i] )):
            return Status.BAD_TRACK_TYPE

        #internal names are empty
        if(internal_names[i] == ''):
            return Status.BAD_INTERNAL_NAME

        #internal names are letters-only
        if(not internal_names[i].isalpha()):
            return Status.BAD_INTERNAL_NAME

        #internal names are all lowercase
        if(not internal_names[i].islower()):
            return Status.BAD_INTERNAL_NAME

    #if pack icon is provided
    if(not packpng == ''):
        #image file still exists
        if(not os.path.isfile(packpng)):
            return Status.PACK_IMAGE_MISSING

        #image is .png
        if(not ('.png' in packpng)):
            return Status.BAD_PACK_IMAGE_TYPE

    return Status.SUCCESS



def convert_to_ogg(track_file, internal_name, create_tmp=True, cleanup_tmp=False):
    #FFmpeg object
    ffmpeg = pyffmpeg.FFmpeg()

    #create temp work directory
    if create_tmp:
        shutil.rmtree(tmp_path, ignore_errors=True)
        os.makedirs(tmp_path)

    track = track_file[0]

    #skip files already in .ogg format
    if '.ogg' in track:
        return Status.SUCCESS

    #rename file so FFmpeg can process it
    track_ext = track.split('/')[-1].split('.')[-1]
    tmp_track = os.path.join(tmp_path, internal_name + '.' + track_ext)

    out_name = internal_name + '.ogg'
    out_track = os.path.join(tmp_path, out_name)

    #copy file to temp work directory and convert
    shutil.copyfile(track, tmp_track)
    ffmpeg.convert(tmp_track, out_track)

    #exit if file was not converted successfully
    if not os.path.isfile(out_track):
        return Status.BAD_OGG_CONVERT

    #change file reference to new converted file
    track_file[0] = out_track

    #usually won't clean up temp work directory here, wait until resource pack generation
    if cleanup_tmp:
        shutil.rmtree(tmp_path, ignore_errors=True)

    return Status.SUCCESS



def generate_datapack(texture_files, track_files, titles, internal_names, user_settings={}):
    #build datapack directory tree
    shutil.rmtree(datapack_name, ignore_errors=True)
    os.makedirs(os.path.join(datapack_name, 'data', 'minecraft', 'tags', 'functions'))
    os.makedirs(os.path.join(datapack_name, 'data', 'minecraft', 'loot_tables', 'entities'))
    os.makedirs(os.path.join(datapack_name, 'data', datapack_name, 'functions'))
    
    #write 'pack.mcmeta'
    pack = open(os.path.join(datapack_name, 'pack.mcmeta'), 'w')
    pack.write(json.dumps({'pack':{'pack_format':pack_format, 'description':(datapack_desc % len(internal_names))}}, indent=4))
    pack.close()
    
    #write 'load.json'
    load = open(os.path.join(datapack_name, 'data', 'minecraft', 'tags', 'functions', 'load.json'), 'w')
    load.write(json.dumps({'values':['{}:setup_load'.format(datapack_name)]}, indent=4))
    load.close()
    
    #write 'tick.json'
    tick = open(os.path.join(datapack_name, 'data', 'minecraft', 'tags', 'functions', 'tick.json'), 'w')
    tick.write(json.dumps({'values':['{}:detect_play_tick'.format(datapack_name), '{}:detect_stop_tick'.format(datapack_name)]}, indent=4))
    tick.close()
    
    
    #write 'setup_load.mcfunction'
    setup_load = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'setup_load.mcfunction'), 'w')
    setup_load.writelines(['scoreboard objectives add usedDisc minecraft.used:minecraft.music_disc_11\n',
                           'scoreboard objectives add heldDisc dummy\n',
                           '\n',
                           'tellraw @a {"text":"Custom Music Discs v1.8 by link2_thepast","color":"yellow"}\n'])
    setup_load.close()
    
    #write 'detect_play_tick.mcfunction'
    detect_play_tick = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'detect_play_tick.mcfunction'), 'w')
    detect_play_tick.writelines(['execute as @a[scores={usedDisc=0}] run scoreboard players set @s heldDisc -1\n',
                                 'execute as @a[scores={usedDisc=0},nbt={Inventory:[{Slot:-106b,id:"minecraft:music_disc_11"}]}] store result score @s heldDisc run data get entity @s Inventory[{Slot:-106b}].tag.CustomModelData\n',
                                 'execute as @a[scores={usedDisc=0},nbt={SelectedItem:{id:"minecraft:music_disc_11"}}] store result score @s heldDisc run data get entity @s SelectedItem.tag.CustomModelData\n',
                                 'execute as @a[scores={usedDisc=2}] run function custom_music_discs_dp:disc_play\n',
                                 '\n',
                                 'execute as @a run scoreboard players add @s usedDisc 0\n',
                                 'execute as @a[scores={usedDisc=2..}] run scoreboard players set @s usedDisc 0\n',
                                 'scoreboard players add @a[scores={usedDisc=1}] usedDisc 1\n'])
    detect_play_tick.close()
    
    #write 'disc_play.mcfunction'
    disc_play = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'disc_play.mcfunction'), 'w')
    
    for i, name in enumerate(internal_names):
        i+=1
        
        disc_play.write('execute as @s[scores={heldDisc=%d}] run function %s:play_%s\n' % (i, datapack_name, name))
        
    disc_play.close()
    
    #write 'detect_stop_tick.mcfunction'
    detect_stop_tick = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'detect_stop_tick.mcfunction'), 'w')
    
    detect_stop_tick.writelines(['execute as @e[type=item, nbt={Item:{id:"minecraft:music_disc_11"}}] at @s unless entity @s[tag=old] if block ~ ~-1 ~ minecraft:jukebox run function custom_music_discs_dp:disc_stop\n',
                                 'execute as @e[type=item, nbt={Item:{id:"minecraft:music_disc_11"}}] at @s unless entity @s[tag=old] if block ~ ~ ~ minecraft:jukebox run function custom_music_discs_dp:disc_stop\n',
                                 'execute as @e[type=item, nbt={Item:{id:"minecraft:music_disc_11"}}] at @s unless entity @s[tag=old] run tag @s add old\n'])
    detect_stop_tick.close()
    
    #write 'disc_stop.mcfunction'
    disc_stop = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'disc_stop.mcfunction'), 'w')
    
    for i, name in enumerate(internal_names):
        i+=1
        
        disc_stop.write('execute as @s[nbt={Item:{tag:{CustomModelData:%d}}}] at @s run stopsound @a[distance=..64] record minecraft:music_disc.%s\n' % (i, name))
    
    disc_stop.close()
    
    #write 'set_disc_track.mcfunction'
    set_disc_track = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'set_disc_track.mcfunction'), 'w')
    
    for i, track in enumerate(titles):
        i+=1
        
        set_disc_track.write('execute as @s[nbt={SelectedItem:{id:"minecraft:music_disc_11", tag:{CustomModelData:%d}}}] run item replace entity @s weapon.mainhand with minecraft:music_disc_11{CustomModelData:%d, HideFlags:32, display:{Lore:[\"\\\"\\\\u00a77%s\\\"\"]}}\n' % (i, i, track.replace('"', '')))
    
    set_disc_track.close()
    
    #write 'play_*.mcfunction' files
    for i, name in enumerate(internal_names):
        play = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'play_%s.mcfunction' % name), 'w')
        play.writelines(['execute as @s at @s run title @a[distance=..64] actionbar {"text":"Now Playing: %s","color":"green"}\n' % (titles[i].replace('"', '')),
                         'execute as @s at @s run stopsound @a[distance=..64] record minecraft:music_disc.11\n',
                         'execute as @s at @s run playsound minecraft:music_disc.%s record @a[distance=..64] ~ ~ ~ 4 1\n' % name])
        play.close()
    
    #write 'creeper.json'
    creeper = open(os.path.join(datapack_name, 'data', 'minecraft', 'loot_tables', 'entities', 'creeper.json'), 'w')
    
    creeper_mdentries = []
    creeper_mdentries.append({'type':'minecraft:tag', 'weight':1, 'name':'minecraft:creeper_drop_music_discs', 'expand':True})
    for i, track in enumerate(titles):
        i+=1
        
        creeper_mdentries.append({'type':'minecraft:item', 'weight':1, 'name':'minecraft:music_disc_11', 'functions':[{'function':'minecraft:set_nbt', 'tag':'{CustomModelData:%d, HideFlags:32, display:{Lore:[\"\\\"\\\\u00a77%s\\\"\"]}}' % (i, track.replace('"', ''))}]})
    
    creeper_normentries = [{'type':'minecraft:item','functions':[{'function':'minecraft:set_count', 'count':{'min':0.0, 'max':2.0, 'type':'minecraft:uniform'}}, {'function':'minecraft:looting_enchant', 'count':{'min':0.0, 'max':1.0}}], 'name':'minecraft:gunpowder'}]
    creeper.write(json.dumps({'type':'minecraft:entity', 'pools':[{'rolls':1, 'entries':creeper_normentries}, {'rolls':1, 'entries':creeper_mdentries, 'conditions':[{'condition':'minecraft:entity_properties', 'predicate':{'type':'#minecraft:skeletons'}, 'entity':'killer'}]}]}, indent=4))
    creeper.close()

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



def generate_resourcepack(texture_files, track_files, titles, internal_names, user_settings={}, cleanup_tmp=True):
    #build resourcepack directory tree
    shutil.rmtree(resourcepack_name, ignore_errors=True)
    os.makedirs(os.path.join(resourcepack_name, 'assets', 'minecraft', 'models', 'item'))
    os.makedirs(os.path.join(resourcepack_name, 'assets', 'minecraft', 'sounds', 'records'))
    os.makedirs(os.path.join(resourcepack_name, 'assets', 'minecraft', 'textures', 'item'))
    
    #write 'pack.mcmeta'
    pack = open(os.path.join(resourcepack_name, 'pack.mcmeta'), 'w')
    pack.write(json.dumps({'pack':{'pack_format':pack_format, 'description':(resourcepack_desc % len(internal_names))}}, indent=4))
    pack.close()
    
    #write 'sounds.json'
    pack = open(os.path.join(resourcepack_name, 'assets', 'minecraft', 'sounds.json'), 'w')
    pack.write('{')
    
    for i, name in enumerate(internal_names):
        pack.write('\n"music_disc.{}": '.format(name))
        pack.write(json.dumps({'sounds': [{'name': 'records/{}'.format(name), 'stream':True}]}, indent=4))
        
        if i < len(internal_names)-1:
            pack.write(',\n')
    
    pack.write('\n}')
    pack.close()
    
    #write 'music_disc_11.json'
    music_disc_11 = open(os.path.join(resourcepack_name, 'assets', 'minecraft', 'models', 'item', 'music_disc_11.json'), 'w')
    
    json_list = []
    for i, name in enumerate(internal_names):
        i+=1
        
        json_list.append({'predicate': {'custom_model_data':i}, 'model': 'item/music_disc_{}'.format(name)})
    
    music_disc_11.write(json.dumps({'parent': 'item/generated', 'textures': {'layer0': 'item/music_disc_11'}, 'overrides': json_list}, indent=4))
    music_disc_11.close()
    
    #write 'music_disc_*.json' files
    for name in internal_names:
        music_disc = open(os.path.join(resourcepack_name, 'assets', 'minecraft', 'models', 'item', 'music_disc_%s.json' % name), 'w')
        music_disc.write(json.dumps({'parent': 'item/generated', 'textures': {'layer0': 'item/music_disc_{}'.format(name)}}, indent=4))
        music_disc.close()
    
    #copy sound and texture files
    for i, name in enumerate(internal_names):
        shutil.copyfile(track_files[i], os.path.join(resourcepack_name, 'assets', 'minecraft', 'sounds', 'records', '%s.ogg' % name))
        shutil.copyfile(texture_files[i], os.path.join(resourcepack_name, 'assets', 'minecraft', 'textures', 'item', 'music_disc_%s.png' % name))
    
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
        shutil.rmtree(tmp_path, ignore_errors=True)
    
    return Status.SUCCESS


