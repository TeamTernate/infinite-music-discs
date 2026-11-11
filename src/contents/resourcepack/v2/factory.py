# -*- coding: utf-8 -*-
#
#Infinite Music Discs resourcepack contents factory module
#Generation tool, datapack design, and resourcepack design by link2_thepast

from src.contents.virtual_factories import VirtualPackFactory
from src.contents.resourcepack.v2.v2p0 import ResourcepackContents_v2p0
from src.contents.resourcepack.v2.v2p1 import ResourcepackContents_v2p1
from src.contents.resourcepack.v2.v2p2 import ResourcepackContents_v2p2

class Resourcepackv2Factory(VirtualPackFactory):

    versions = [
        ResourcepackContents_v2p0,
        ResourcepackContents_v2p1,
        ResourcepackContents_v2p2
    ]
