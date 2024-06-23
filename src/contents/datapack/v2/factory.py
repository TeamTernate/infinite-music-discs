# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack contents factory module
#Generation tool, datapack design, and resourcepack design by link2_thepast

from src.contents.virtual_factories import VirtualPackFactory
from src.contents.datapack.v2.v2p0 import DatapackContents_v2p0
from src.contents.datapack.v2.v2p1 import DatapackContents_v2p1
from src.contents.datapack.v2.v2p2 import DatapackContents_v2p2
from src.contents.datapack.v2.v2p3 import DatapackContents_v2p3

class Datapackv2Factory(VirtualPackFactory):

    versions = [
        DatapackContents_v2p0,
        DatapackContents_v2p1,
        DatapackContents_v2p2,
        DatapackContents_v2p3
    ]
