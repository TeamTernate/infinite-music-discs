# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack template class
#Generation tool, datapack design, and resourcepack design by link2_thepast

# Virtual class that forms the beginning of a chain of classes that
#   inherit each other to define the datapack contents
# virtual -> v2.0 -> v2.1 -> ...
class VirtualDatapackContents():

    def __init__(self):
        self.add_contents()

    def add_contents(self):
        pass

    #use list comprehension to collect the contents of all instance attributes in
    #  self.__dict__ (returns a list of all 'self.x' variables from this class instance)
    @property
    def contents(self):
        attr_dict = self.__dict__
        return [attr_dict[k] for k in attr_dict \
                if not k.startswith('__') and not callable(getattr(self, k))]


