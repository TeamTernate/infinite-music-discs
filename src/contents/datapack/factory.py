# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack contents abstract factory module
#Generation tool, datapack design, and resourcepack design by link2_thepast

import src.contents.datapack.v2.factory as v2_factory
#import src.contents.datapack.v3.factory as v3_factory

# Abstract factory to select which datapack factory should be used to generate
#   the datapack based on the version the user wants. Returns the DatapackContents
#   from the chosen factory
def get(pack_format: int, datapack_version: int):
    if(datapack_version == 2):
        return v2_factory.get(pack_format)
    # else:
        # return v3_factory.get(pack_format)
