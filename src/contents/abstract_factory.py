# -*- coding: utf-8 -*-
#
#Infinite Music Discs pack contents abstract factory module
#Generation tool, datapack design, and resourcepack design by link2_thepast



# Abstract factory decides which major version to use during pack generation
#   by picking the appropriate sub-factory. Each major version defines its own
#   sub-factory which picks the actual instance
# The datapack will register datapack factories with its copy of this abstract
#   factory same for the resourcepack with its abstract factory
# TODO: can static classes have @properties? Would be nice not to have to instantiate these, save memory
class VirtualAbstractPackFactory():

    factories = []

    # Return an instance of VirtualPackContents (or a derived class)
    #   selected by one of the factories
    def get(self, pack_format: int):
        for f in self.factories:
            if f.min_pack_format <= pack_format:
                sel_factory = f

        return sel_factory.get(pack_format)


