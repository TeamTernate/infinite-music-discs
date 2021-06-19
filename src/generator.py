#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack + resourcepack generator module
#Script, datapack design, and resourcepack design by link2_thepast
#
#Generates datapack v1.8

import os
import json
import shutil
import sys

datapack_name = 'custom_music_discs_dp'
resourcepack_name = 'custom_music_discs_rp'

datapack_desc = 'Adds %d custom music discs'
resourcepack_desc = 'Adds %d custom music discs'

pack_format = 7



def validate(texture_files, track_files, titles, internal_names):
    #lists are all the same length
    if(not ( len(texture_files) == len(track_files) == len(titles) == len(internal_names) )):
        return 1

    #lists are not empty
    if(len(texture_files) == 0):
        return 1

    for i in range(len(texture_files)):
        #images are all .png
        if(not ( '.png' in texture_files[i] )):
            return 1

        #tracks are all .mp3, .wav, .ogg
        if(not ( '.mp3' in track_files[i] or '.wav' in track_files[i] or '.ogg' in track_files[i] )):
            return 1

        #internal names are letters-only
        if(not internal_names[i].isalpha()):
            return 1

        #internal names are all lowercase
        if(not internal_names[i].islower()):
            return 1
        
    return 0



def generate_datapack(texture_files, track_files, titles, internal_names):
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
    
    return 0


