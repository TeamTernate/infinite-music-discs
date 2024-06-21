# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack contents abstract factory module
#Generation tool, datapack design, and resourcepack design by link2_thepast

from src.contents.virtual_factories import VirtualAbstractPackFactory
from src.contents.datapack.v2.factory import Datapackv2Factory
from src.contents.datapack.v3.factory import Datapackv3Factory

class AbstractDatapackFactory(VirtualAbstractPackFactory):

    factories = [
        Datapackv2Factory(),
        Datapackv3Factory()
    ]
