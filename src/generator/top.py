#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack + resourcepack generator module
#Generation tool, datapack design, and resourcepack design by link2_thepast

from src.generator.v1 import GeneratorV1

#TODO: design this to be split into multiple variants for v1.x and v2.x
#TODO: create generator_wrapper.py that handles all the status and validation stuff, and have
#   generator_v1.py and generator_v2.py to handle datapack creation?

def get_generator():
    return GeneratorV1()

    # if(True):
    #     return GeneratorV1()
    # else:
    #     return GeneratorV2()


