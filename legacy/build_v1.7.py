#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#Custom Music Discs datapack + resourcepack generator script
#Script, datapack design, and resourcepack design by link2_thepast
#
#Script v1.3
#Datapack v1.7

import os
import json
import shutil
import sys

datapack_name = 'custom_music_discs_dp'
resourcepack_name = 'custom_music_discs_rp'

datapack_desc = 'Adds %d custom music discs'
resourcepack_desc = 'Adds %d custom music discs'

print("Generating datapack...")


file_list = [f for f in os.listdir(".") if os.path.isfile(f)]
song_list = []
texture_list = []
name_list = []
track_list = []

#check for resource files
for f in file_list:
    if '.ogg' in f:
        try:
            int(f.split('.')[0])
            song_list.append(f)
        except ValueError:
            pass
        
    elif '.png' in f:
        try:
            int(f.split('.')[0])
            texture_list.append(f)
        except ValueError:
            pass
        
    elif 'internal_names.txt' == f:
        file = open(f, 'r')
        name_list = file.read().splitlines()
        file.close()
        
    elif 'track_names.txt' == f:
        file = open(f, 'r')
        track_list = file.read().splitlines()
        file.close()

#basic error catching, onus is on the user to follow the right formats
if len(track_list) != len(name_list):
    print("Error: Number of track names does not match the number of internal names. Make sure each internal name has a track name.")
    quit()

if len(song_list) < len(name_list):
    print("Error: Could not find enough music files. Make sure all tracks are in .ogg format and have the appropriate numerical name.")
    quit()

elif len(song_list) > len(name_list):
    print("Error: Found more music files than internal names. Make sure each track has a track name and an internal name.")
    quit()

if len(texture_list) < len(name_list):
    print("Error: Could not find enough texture files. Make sure all textures are in .png format and have the appropriate numerical name.")
    quit()

elif len(texture_list) > len(name_list):
    print("Error: Found more texture files than internal names. Make sure each track has a track name and an internal name.")
    quit()

print("Found %d tracks..." % len(name_list))

""" -- BUILD DATAPACK -- """
#build datapack directory tree
shutil.rmtree(datapack_name, ignore_errors=True)
os.makedirs(os.path.join(datapack_name, 'data', 'minecraft', 'tags', 'functions'))
os.makedirs(os.path.join(datapack_name, 'data', 'minecraft', 'loot_tables', 'entities'))
os.makedirs(os.path.join(datapack_name, 'data', datapack_name, 'functions'))

#write 'pack.mcmeta'
pack = open(os.path.join(datapack_name, 'pack.mcmeta'), 'w')
pack.write(json.dumps({'pack':{'pack_format':4, 'description':(datapack_desc % len(name_list))}}, indent=4))
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
                       'tellraw @a {"text":"Custom Music Discs v1.7 by link2_thepast","color":"yellow"}\n'])
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

for i, name in enumerate(name_list):
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

for i, name in enumerate(name_list):
    i+=1
    
    disc_stop.write('execute as @s[nbt={Item:{tag:{CustomModelData:%d}}}] at @s run stopsound @a[distance=..64] record minecraft:music_disc.%s\n' % (i, name))

disc_stop.close()

#write 'set_disc_track.mcfunction'
set_disc_track = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'set_disc_track.mcfunction'), 'w')

for i, track in enumerate(track_list):
    i+=1
    
    set_disc_track.write('execute as @s[nbt={SelectedItem:{id:"minecraft:music_disc_11", tag:{CustomModelData:%d}}}] run replaceitem entity @s weapon.mainhand minecraft:music_disc_11{CustomModelData:%d, HideFlags:32, display:{Lore:[\"\\\"\\\\u00a77%s\\\"\"]}}\n' % (i, i, track.replace('"', '')))

set_disc_track.close()

#write 'play_*.mcfunction' files
for i, name in enumerate(name_list):
    play = open(os.path.join(datapack_name, 'data', datapack_name, 'functions', 'play_%s.mcfunction' % name), 'w')
    play.writelines(['execute as @s at @s run title @a[distance=..64] actionbar {"text":"Now Playing: %s","color":"green"}\n' % (track_list[i].replace('"', '')),
                     'execute as @s at @s run stopsound @a[distance=..64] record minecraft:music_disc.11\n',
                     'execute as @s at @s run playsound minecraft:music_disc.%s record @a[distance=..64] ~ ~ ~ 4 1\n' % name])
    play.close()

#write 'creeper.json'
creeper = open(os.path.join(datapack_name, 'data', 'minecraft', 'loot_tables', 'entities', 'creeper.json'), 'w')

creeper_mdentries = []
creeper_mdentries.append({'type':'minecraft:tag', 'weight':1, 'name':'minecraft:creeper_drop_music_discs', 'expand':True})
for i, track in enumerate(track_list):
    i+=1
    
    creeper_mdentries.append({'type':'minecraft:item', 'weight':1, 'name':'minecraft:music_disc_11', 'functions':[{'function':'minecraft:set_nbt', 'tag':'{CustomModelData:%d, HideFlags:32, display:{Lore:[\"\\\"\\\\u00a77%s\\\"\"]}}' % (i, track.replace('"', ''))}]})

creeper_normentries = [{'type':'minecraft:item','functions':[{'function':'minecraft:set_count', 'count':{'min':0.0, 'max':2.0, 'type':'minecraft:uniform'}}, {'function':'minecraft:looting_enchant', 'count':{'min':0.0, 'max':1.0}}], 'name':'minecraft:gunpowder'}]
creeper.write(json.dumps({'type':'minecraft:entity', 'pools':[{'rolls':1, 'entries':creeper_normentries}, {'rolls':1, 'entries':creeper_mdentries, 'conditions':[{'condition':'minecraft:entity_properties', 'predicate':{'type':'#minecraft:skeletons'}, 'entity':'killer'}]}]}, indent=4))
creeper.close()


""" -- BUILD RESOURCEPACK -- """
#build resourcepack directory tree
shutil.rmtree(resourcepack_name, ignore_errors=True)
os.makedirs(os.path.join(resourcepack_name, 'assets', 'minecraft', 'models', 'item'))
os.makedirs(os.path.join(resourcepack_name, 'assets', 'minecraft', 'sounds', 'records'))
os.makedirs(os.path.join(resourcepack_name, 'assets', 'minecraft', 'textures', 'item'))

#write 'pack.mcmeta'
pack = open(os.path.join(resourcepack_name, 'pack.mcmeta'), 'w')
pack.write(json.dumps({'pack':{'pack_format':6, 'description':(resourcepack_desc % len(name_list))}}, indent=4))
pack.close()

#write 'sounds.json'
pack = open(os.path.join(resourcepack_name, 'assets', 'minecraft', 'sounds.json'), 'w')
pack.write('{')

for i, name in enumerate(name_list):
    pack.write('\n"music_disc.{}": '.format(name))
    pack.write(json.dumps({'sounds': [{'name': 'records/{}'.format(name), 'stream':True}]}, indent=4))

    if i < len(name_list)-1:
        pack.write(',\n')

pack.write('\n}')
pack.close()

#write 'music_disc_11.json'
music_disc_11 = open(os.path.join(resourcepack_name, 'assets', 'minecraft', 'models', 'item', 'music_disc_11.json'), 'w')

json_list = []
for i, name in enumerate(name_list):
    i+=1
    
    json_list.append({'predicate': {'custom_model_data':i}, 'model': 'item/music_disc_{}'.format(name)})

music_disc_11.write(json.dumps({'parent': 'item/generated', 'textures': {'layer0': 'item/music_disc_11'}, 'overrides': json_list}, indent=4))
music_disc_11.close()

#write 'music_disc_*.json' files
for name in name_list:
    music_disc = open(os.path.join(resourcepack_name, 'assets', 'minecraft', 'models', 'item', 'music_disc_%s.json' % name), 'w')
    music_disc.write(json.dumps({'parent': 'item/generated', 'textures': {'layer0': 'item/music_disc_{}'.format(name)}}, indent=4))
    music_disc.close()

#copy sound and texture files
for i, name in enumerate(name_list):
    i+=1
    
    shutil.copyfile('%d.ogg' % i, os.path.join(resourcepack_name, 'assets', 'minecraft', 'sounds', 'records', '%s.ogg' % name))
    shutil.copyfile('%d.png' % i, os.path.join(resourcepack_name, 'assets', 'minecraft', 'textures', 'item', 'music_disc_%s.png' % name))

#copy pack.png
try:
    shutil.copyfile('pack.png', os.path.join(resourcepack_name, 'pack.png'))
    shutil.copyfile('pack.png', os.path.join(datapack_name, 'pack.png'))
except IOError:
    print("Warning: No pack.png found. Your resourcepack will not have an icon.")


print("\nDone! Place '%s' into your '.minecraft/resourcepacks' folder, and place '%s' into your save's 'datapacks' folder." % (resourcepack_name, datapack_name))
