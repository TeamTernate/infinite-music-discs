# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack contents factory module
#Generation tool, datapack design, and resourcepack design by link2_thepast

from src.contents.virtual_factories import VirtualPackFactory
from src.contents.datapack.v3.v3p0 import DatapackContents_v3p0

class Datapackv3Factory(VirtualPackFactory):

    versions = [
        DatapackContents_v3p0
    ]
