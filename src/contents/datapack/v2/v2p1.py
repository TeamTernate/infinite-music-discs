# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack v2.1 contents
#Generation tool, datapack design, and resourcepack design by link2_thepast

from src.contents.datapack.v2.v2p0 import DatapackContents_v2p0



# advancements
placed_disc = {
    'path': ['data', '{datapack_name}', 'advancements', 'placed_disc.json'],
    'repeat': 'single',
    'contents': \
{
  "criteria": {
    "placed_music_disc": {
      "trigger": "minecraft:item_used_on_block",
      "conditions": {
        "location": [
            {
                "condition": "minecraft:location_check",
                "predicate": {
                    "block": {
                        "blocks": [ "minecraft:jukebox" ],
                        "state": { "has_record":"true" }
                    }
                }
            }
        ],
        "item": {
          "tag": "minecraft:music_discs"
        }
      }
    }
  },
  "rewards": {
    "function": "{datapack_name}:on_placed_disc"
  }
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
        "location": [
            {
                "condition": "minecraft:location_check",
                "predicate": {
                    "block": {
                        "blocks": [ "minecraft:jukebox" ]
                    }
                }
            }
        ]
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


