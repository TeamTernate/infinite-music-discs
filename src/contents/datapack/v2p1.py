# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack v2.0 contents
#Generation tool, datapack design, and resourcepack design by link2_thepast

from src.contents.datapack.v2p0 import DatapackContents_v2p0



# advancements
placed_disc = {
    'path': ['data', '{datapack_name}', 'advancements', 'placed_disc.json'],
    'repeat': 'single',
    'contents': \
{
  "yay": "it works"
}
}

placed_jukebox = {
    'path': ['data', '{datapack_name}', 'advancements', 'placed_jukebox.json'],
    'repeat': 'single',
    'contents': \
{
  "criteria": {
    "placed_jukebox": {
      "trigger": "minecraft:placed_block",
      "conditions": {
        "block": "minecraft:jukebox",
        "item": {
          "items": [ "minecraft:jukebox" ]
        }
      }
    }
  },
  "rewards": {
    "function": "{datapack_name}:on_placed_jukebox"
  }
}
}



# See src.contents.datapack.v2p0 for info on this class structure
class DatapackContents_v2p1(DatapackContents_v2p0):

    min_pack_format = 15
    version_major = 2
    version_minor = 1

    def add_contents(self):
        super().add_contents()

        self.placed_disc = placed_disc
        self.placed_jukebox = placed_jukebox


