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
    pass
