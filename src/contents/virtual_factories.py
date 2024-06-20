# -*- coding: utf-8 -*-
#
#Infinite Music Discs contents virtual factory module
#Generation tool, datapack design, and resourcepack design by link2_thepast

# See src.contents.datapack.v2.factory for a concrete factory implementation
# See src.contents.datapack.factory for an abstract factory implementation
# See src.generator.v2 for an example of how to use the abstract factory
# TODO: can static classes have @properties? Would be nice not to have to instantiate these, save memory

# Virtual implementation of a concrete "pack factory"
#
# Pack factories are used to select between different DatapackContents or
#   ResourcepackContents. Uses pack_format to pick which version to use,
#   and returns an instance of the selected class
# If 'versions' is sorted in ascending order (v0 -> v1 -> v2 -> etc)
#   then the factory will pick the latest pack version compatible
#   with the given pack_format and return an instance of it
class VirtualPackFactory():

    versions = []

    @property
    def min_pack_format(self):
        return self.versions[0].min_pack_format

    def get(self, pack_format: int):
        for v in self.versions:
            if v.min_pack_format <= pack_format:
                sel_version = v

        return sel_version()



# Abstract factory decides which major version to use during pack generation
#   by picking the appropriate sub-factory. Each major version defines its own
#   concrete sub-factory (an instance of the pack factory above) and that factory
#   picks the actual VirtualPackContents instance to return
# If 'factories' is sorted in ascending order (min_pack_format properties are ascending)
#   then the abstract factory will pick the latest factory compatible with the given
#   pack_format
class VirtualAbstractPackFactory():

    factories = []

    # Return an instance of VirtualPackContents (or a derived class)
    #   selected by one of the factories
    def get(self, pack_format: int):
        for f in self.factories:
            if f.min_pack_format <= pack_format:
                sel_factory = f

        return sel_factory.get(pack_format)


