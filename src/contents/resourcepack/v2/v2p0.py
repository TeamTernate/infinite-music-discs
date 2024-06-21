# -*- coding: utf-8 -*-
#
#Infinite Music Discs resourcepack v1.0 contents
#Generation tool, datapack design, and resourcepack design by link2_thepast

from src.contents.base import VirtualPackContents



# pack.mcmeta
pack_mcmeta = {
    'path': ['pack.mcmeta'],
    'repeat': 'single',
    'contents': \
{
    "pack": {
        "pack_format": '(int){pack_format}',
        "description": "Adds {rp_num_discs} custom music discs"
    }
}
}

# minecraft namespace
# atlases/blocks.json
blocks_json = {
    'path': ['assets', 'minecraft', 'atlases', 'blocks.json'],
    'repeat': 'single',
    'contents': \
{
    "sources": [
        {
            "type": "directory",
            "source": "item",
            "prefix": "item/"
        }
    ]
}
}

# models/item/music_disc_11.json
music_disc_11_entries = []

music_disc_11_entry = {
    "predicate": {
        "custom_model_data": '(int){entry.custom_model_data}'
    },
    "model": "{pack_name}:item/music_disc_{entry.internal_name}"
}

music_disc_11_json = {
    'path': ['assets', 'minecraft', 'models', 'item', 'music_disc_11.json'],
    'repeat': 'single',
    'contents': \
{
    "parent": "item/generated",
    "textures": {
        "layer0": "item/music_disc_11"
    },
    "overrides": music_disc_11_entries
}
}

# pack namespace
# sounds.json
sounds_json_entries = {}

sounds_json_entry = {
    "music_disc.{entry.internal_name}": {
        "sounds": [
            {
                "name": "{pack_name}:records/{entry.internal_name}",
                "stream": True
            }
        ]
    }
}

sounds_json = {
    'path': ['assets', '{pack_name}', 'sounds.json'],
    'repeat': 'single',
    'contents': sounds_json_entries
}

# models/item/music_disc_<track>.json
music_disc_track_json = {
    'path': ['assets', '{pack_name}', 'models', 'item', 'music_disc_{entry.internal_name}.json'],
    'repeat': 'copy',
    'contents': \
{
    "parent": "item/generated",
    "textures": {
        "layer0": "{pack_name}:item/music_disc_{entry.internal_name}"
    }
}
}

# asset file locations
#TODO: use 'copy' and above formatting for these?
sound_path = ['assets', '{pack_name}', 'sounds', 'records']
texture_path = ['assets', '{pack_name}', 'textures', 'item']



# See src.contents.datapack.v2.v2p0 for info on this class structure
class ResourcepackContents_v2p0(VirtualPackContents):

    min_pack_format = 34
    version_major = 2
    version_minor = 0

    #all files except sounds.json and music_disc_11.json
    #those files are more complicated and require extra effort
    def add_contents(self):
        self.blocks_json = blocks_json
        self.music_disc_track_json = music_disc_track_json
        self.pack_mcmeta = pack_mcmeta

    @property
    def version_str(self):
        return f"v{self.version_major}.{self.version_minor}"

    #sounds.json
    def get_sounds_json_entry(self):
        return sounds_json_entry

    def get_sounds_json(self, sounds_json_entries: dict):
        #reach inside and set the music disc entries manually since it's
        #  hard to elegantly generate this file
        sounds_json['contents'] = sounds_json_entries
        return sounds_json

    #music_disc_11.json
    def get_music_disc_11_entry(self):
        return music_disc_11_entry

    def get_music_disc_11_json(self, music_disc_11_entries: list):
        music_disc_11_json['contents']['overrides'] = music_disc_11_entries
        return music_disc_11_json

    #asset file locations
    def get_sound_path(self):
        return sound_path

    def get_texture_path(self):
        return texture_path
