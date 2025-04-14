# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack contents factory module
#Generation tool, datapack design, and resourcepack design by link2_thepast

from src.contents.virtual_factories import VirtualPackFactory
from src.contents.datapack.v3.v3p0 import DatapackContents_v3p0
from src.contents.datapack.v3.v3p1 import DatapackContents_v3p1
from src.contents.datapack.v3.v3p2 import DatapackContents_v3p2
from src.contents.datapack.v3.v3p3 import DatapackContents_v3p3

class Datapackv3Factory(VirtualPackFactory):

    versions = [
        DatapackContents_v3p0,
        DatapackContents_v3p1,
        DatapackContents_v3p2,
        DatapackContents_v3p3
    ]
