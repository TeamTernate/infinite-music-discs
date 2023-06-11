# reserved for future use - not currently used because
#   resourcepack generation is so different from datapack generation

# pack.mcmeta
pack_mcmeta = {
    'path': ['{resourcepack_name}', 'pack.mcmeta'],
    'repeat': 'single',
    'contents': \
{
    'pack': {
        'pack_format': -1,
        'description': "Adds {rp_num_discs} custom music discs"
    }
}
}

# sounds.json
sounds_entry_key = "music_disc.{entry.internal_name}"

sounds_entry = {
    "sounds": [
        {
            "name": "records/{entry.internal_name}",
            "stream": True
        }
    ]
}

sounds_json = {
    'path': ['{resourcepack_name}', 'assets', 'minecraft', 'sounds.json'],
    'repeat': 'single',
    'contents': \
{

}
}

# music_disc_11.json
music_disc_11_overrides = []

music_disc_11_override = {
    'predicate': {'custom_model_data': -1},
    'model': 'item/music_disc_{entry.internal_name}'
}

music_disc_11_json = {
    'path': ['{resourcepack_name}', 'assets', 'minecraft', 'models', 'item', 'music_disc_11.json'],
    'repeat': 'single',
    'contents': \
{
    'parent': 'item/generated',
    'textures': {
        'layer0': 'item/music_disc_11'
    },
    'overrides': music_disc_11_overrides
}
}

# iterable list of files
file_list = [
    pack_mcmeta,
    sounds_json,
    music_disc_11_json
]
