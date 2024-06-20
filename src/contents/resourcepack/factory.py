# -*- coding: utf-8 -*-
#
#Infinite Music Discs resourcepack contents abstract factory module
#Generation tool, datapack design, and resourcepack design by link2_thepast

from src.contents.virtual_factories import VirtualAbstractPackFactory
from src.contents.resourcepack.v1.factory import Resourcepackv1Factory
from src.contents.resourcepack.v2.factory import Resourcepackv2Factory

class AbstractResourcepackFactory(VirtualAbstractPackFactory):

    factories = [
        Resourcepackv1Factory(),
        Resourcepackv2Factory()
    ]
