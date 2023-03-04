#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack + resourcepack generator module
#Generation tool, datapack design, and resourcepack design by link2_thepast
#
#Generates datapack v1.9

import os
import json
import shutil
import sys
import zipfile
import pyffmpeg
import tempfile

from mutagen.mp3 import MP3, HeaderNotFoundError
from mutagen.oggvorbis import OggVorbis
from src.definitions import Status, GeneratorContents, DiscListContents, DiscListEntryContents
from src.commands import ReplaceItemCommand, ItemSlot

default_pack_name = 'infinite_music_discs'

datapack_suffix = '_dp'
resourcepack_suffix = '_rp'
zip_suffix = '.zip'

datapack_desc = 'Adds %d custom music discs'
resourcepack_desc = 'Adds %d custom music discs'
default_pack_format = 8     #TODO: can this come from definitions?

tmp_path = None

#TODO: design this to be split into multiple variants for v1.x and v2.x
#TODO: create generator_wrapper.py that handles all the status and validation stuff, and have
#   generator_v1.py and generator_v2.py to handle datapack creation?



def validate(generator_data: GeneratorContents):
    global tmp_path

    packpng = generator_data.settings['pack']

    #lists are not empty
    if(len(generator_data.entry_list) == 0):
        return Status.LIST_EMPTY

    #internal names are all unique
    if( len(generator_data.entry_list.internal_names) > len(set(generator_data.entry_list.internal_names)) ):
        return Status.DUP_INTERNAL_NAME

    for e in generator_data.entry_list.entries:
        #image is provided
        if(e.texture_file == ''):
            return Status.IMAGE_FILE_NOT_GIVEN

        #image files still exist
        if(not os.path.isfile(e.texture_file)):
            return Status.IMAGE_FILE_MISSING

        #images are all .png
        if(not ( '.png' in e.texture_file )):
            return Status.BAD_IMAGE_TYPE

        #track is provided
        if(e.track_file == ''):
            return Status.TRACK_FILE_NOT_GIVEN

        #track files still exist
        if(not os.path.isfile(e.track_file)):
            return Status.TRACK_FILE_MISSING

        #tracks are all .mp3, .wav, .ogg
        if(not ( '.mp3' in e.track_file or '.wav' in e.track_file or '.ogg' in e.track_file )):
            return Status.BAD_TRACK_TYPE

        #internal names are not empty
        if(e.internal_name == ''):
            return Status.BAD_INTERNAL_NAME

        #internal names are letters-only
        if(not e.internal_name.isalpha()):
            return Status.BAD_INTERNAL_NAME

        #internal names are all lowercase
        if(not e.internal_name.islower()):
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



#TODO: use mutagen to detect audio length and save for datapack use
def convert_to_ogg(track_entry: DiscListEntryContents, mix_mono, create_tmp=True, cleanup_tmp=False):
    global tmp_path

    track = track_entry.track_file
    internal_name = track_entry.internal_name

    #FFmpeg object
    ffmpeg = pyffmpeg.FFmpeg()

    #create temp work directory
    if create_tmp:
        if tmp_path != None:
            shutil.rmtree(tmp_path)

        tmp_path = tempfile.mkdtemp()

    #build FFmpeg settings
    args = ''

    if mix_mono:
        args += ' -ac 1'

    #skip files that don't need to be processed
    if args == '' and '.ogg' in track:
        return Status.SUCCESS

    #rename file so FFmpeg can process it
    track_ext = track.split('/')[-1].split('.')[-1]
    tmp_track = os.path.join(tmp_path, internal_name + '.tmp.' + track_ext)

    out_name = internal_name + '.ogg'
    out_track = os.path.join(tmp_path, out_name)

    #copy file to temp work directory
    shutil.copyfile(track, tmp_track)

    #strip any ID3 metadata from mp3
    if '.mp3' in tmp_track:
        try:
            meta_mp3 = MP3(tmp_track)
            meta_mp3.delete()
            meta_mp3.save()
        except HeaderNotFoundError:
            #no metadata to be removed, ignore
            pass

    #exit if metadata removal failed
    if not os.path.isfile(tmp_track):
        return Status.BAD_MP3_META, track

    #convert file
    try:
        ffmpeg.options("-nostdin -y -i %s -c:a libvorbis%s %s" % (tmp_track, args, out_track))

    except Exception as e:
        #TODO: how to reraise exception and also return?
        print(e)
        return Status.FFMPEG_CONVERT_FAIL, track

    #exit if file was not converted successfully
    if not os.path.isfile(out_track):
        return Status.BAD_OGG_CONVERT, track

    if os.path.getsize(out_track) == 0:
        return Status.BAD_OGG_CONVERT, track

    #usually won't clean up temp work directory here, wait until resource pack generation
    if cleanup_tmp:
        shutil.rmtree(tmp_path, ignore_errors=True)
        tmp_path = None

    return Status.SUCCESS, out_track



def get_track_length(track_entry: DiscListEntryContents):
    try:
        #capture track length in seconds
        meta_ogg = OggVorbis(track_entry.track_file)
        length_s = meta_ogg.info.length

        #convert from seconds to Minecraft ticks (20 t/s)
        length_t = int(length_s) * 20

    except Exception as e:
        #TODO: how to reraise exception and also return?
        print(e)
        return Status.BAD_OGG_META, 0

    return Status.SUCCESS, length_t



#TODO: break into smaller functions so it's easier to understand behavior?
def generate_datapack(entry_list: DiscListContents, user_settings={}):
    global tmp_path

    titles = entry_list.titles
    internal_names = entry_list.internal_names

    #read settings
    pack_format = user_settings.get('version').get('dp', default_pack_format)
    offset = user_settings.get('offset', 0)

    datapack_name = user_settings.get('name', default_pack_name)
    datapack_name = datapack_name + datapack_suffix
    datapack_name_zip = datapack_name + zip_suffix

    try:
        #build datapack directory tree
        shutil.rmtree(datapack_name, ignore_errors=True)
        os.makedirs(os.path.join(datapack_name, 'data', 'minecraft', 'tags', 'functions'))
        os.makedirs(os.path.join(datapack_name, 'data', 'minecraft', 'loot_tables', 'entities'))
        os.makedirs(os.path.join(datapack_name, 'data', datapack_name, 'functions'))

        #write 'pack.mcmeta'
        pack = open(os.path.join(datapack_name, 'pack.mcmeta'), 'w', encoding='utf-8')
        pack.write(json.dumps({'pack':{'pack_format':pack_format, 'description':(datapack_desc % len(internal_names))}}, indent=4))
        pack.close()

        #write 'load.json'
        load = open(os.path.join(datapack_name, 'data', 'minecraft', 'tags', 'functions', 'load.json'), 'w', encoding='utf-8')
        load.write(json.dumps({'values':['{}:setup_load'.format(datapack_name)]}, indent=4))
        load.close()

        #write 'tick.json'
        tick = open(os.path.join(datapack_name, 'data', 'minecraft', 'tags', 'functions', 'tick.json'), 'w', encoding='utf-8')
        tick.write(json.dumps({'values':['{}:detect_play_tick'.format(datapack_name), '{}:detect_stop_tick'.format(datapack_name)]}, indent=4))
        tick.close()


        #write 'setup_load.mcfunction'
        setup_load = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'setup_load.mcfunction'), 'w', encoding='utf-8')
        setup_load.writelines(['scoreboard objectives add usedDisc minecraft.used:minecraft.music_disc_11\n',
                               'scoreboard objectives add heldDisc dummy\n',
                               '\n',
                               'tellraw @a {"text":"Infinite Music Discs v1.9 by link2_thepast","color":"yellow"}\n'])
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



def generate_resourcepack(entry_list: DiscListContents, user_settings={}, cleanup_tmp=True):
    global tmp_path

    texture_files = entry_list.texture_files
    track_files = entry_list.track_files
    internal_names = entry_list.internal_names

    #read settings
    pack_format = user_settings.get('version').get('rp', default_pack_format)
    offset = user_settings.get('offset', 0)

    resourcepack_name = user_settings.get('name', default_pack_name)
    resourcepack_name = resourcepack_name + resourcepack_suffix
    resourcepack_name_zip = resourcepack_name + zip_suffix

    try:
        #build resourcepack directory tree
        shutil.rmtree(resourcepack_name, ignore_errors=True)
        os.makedirs(os.path.join(resourcepack_name, 'assets', 'minecraft', 'models', 'item'))
        os.makedirs(os.path.join(resourcepack_name, 'assets', 'minecraft', 'sounds', 'records'))
        os.makedirs(os.path.join(resourcepack_name, 'assets', 'minecraft', 'textures', 'item'))

        #write 'pack.mcmeta'
        pack = open(os.path.join(resourcepack_name, 'pack.mcmeta'), 'w', encoding='utf-8')
        pack.write(json.dumps({'pack':{'pack_format':pack_format, 'description':(resourcepack_desc % len(internal_names))}}, indent=4))
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
        shutil.rmtree(tmp_path, ignore_errors=True)
        tmp_path = None

    return Status.SUCCESS


