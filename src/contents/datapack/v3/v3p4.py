# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack v3.4 contents
#Generation tool, datapack design, and resourcepack design by link2_thepast

from src.contents.datapack.v3.v3p3 import DatapackContents_v3p3

creeper_normal_entries = [
    {
        'type': 'minecraft:item',
        'modifier': [
            {
                'type': 'minecraft:set_count',
                'count': {'type': 'minecraft:uniform', 'max': 2, 'min': 0}
            },
            {
                'type': 'minecraft:enchanted_count_increase',
                'count': {'type': 'minecraft:uniform', 'max': 1.0, 'min': 0.0},
                'enchantment': 'minecraft:looting'
            }
        ],
        'name': 'minecraft:gunpowder'
    }
]

creeper_music_entries = []

creeper_music_entry_base = {
    'type': 'minecraft:tag',
    'weight': 1,
    'items': '#minecraft:creeper_drop_music_discs',
    'expand': True
}

creeper_music_entry_custom = {
    'type': 'minecraft:item',
    'weight': 1,
    'name': 'minecraft:music_disc_11',
    'modifier': [{
        'type': 'minecraft:set_components',
        'components': {
            'minecraft:item_model': '{pack_name}:{entry.internal_name}',
            'minecraft:jukebox_playable': '{pack_name}:{entry.internal_name}'
        }
    }]
}

creeper_json = {
    'path': ['data', 'minecraft', 'loot_table', 'entities', 'creeper.json'],
    'repeat': 'single',
    'format_contents': False,
    'contents': {
        'type': 'minecraft:entity',
        'pools': [
            {'rolls': 1, 'entries': creeper_normal_entries},
            {'rolls': 1, 'entries': creeper_music_entries, 'condition': {
                'type': 'minecraft:entity_properties',
                'entity': 'attacker',
                'predicate': {'minecraft:entity_type': '#minecraft:skeletons'}
            }}
        ],
        'random_sequence': 'minecraft:entities/creeper'
    }
}

class DatapackContents_v3p4(DatapackContents_v3p3):
    min_pack_format = 121
    max_pack_format = 999
    version_major = 3
    version_minor = 4

    def add_contents(self):
        super().add_contents()

        #creeper.json
    def get_creeper_music_entry_base(self):
        return creeper_music_entry_base

    def get_creeper_music_entry_custom(self):
        return creeper_music_entry_custom

    def get_creeper_json(self, creeper_music_entries: list):
        #reach inside and set the music disc entries manually since it's
        #  hard to elegantly generate this file
        creeper_json['contents']['pools'][1]['entries'] = creeper_music_entries
        return creeper_json
