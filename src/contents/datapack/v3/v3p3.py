# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack v3.3 contents
#Generation tool, datapack design, and resourcepack design by link2_thepast

from src.contents.datapack.v3.v3p2 import DatapackContents_v3p2

pack_mcmeta = {
    'path': ['pack.mcmeta'],
    'repeat': 'single',
    'contents': {
        "pack": {
            "min_format": '(int){pack_format}',
            "max_format": '(int){max_pack_format}',
            "description": "Adds {dp_num_discs} custom music discs"
        }
    }
}

class DatapackContents_v3p3(DatapackContents_v3p2):
    min_pack_format = 88
    max_pack_format = 107
    version_major = 3
    version_minor = 3

    def add_contents(self):
        super().add_contents()
        self.pack_mcmeta = pack_mcmeta
