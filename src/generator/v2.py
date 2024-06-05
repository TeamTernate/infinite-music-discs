# -*- coding: utf-8 -*-
#
#Infinite Music Discs generator module implementation
#Generation tool, datapack design, and resourcepack design by link2_thepast
#
#Generates datapack v2.0
from typing import Union, TextIO

import os
import json
import shutil
import zipfile

import src.contents.datapack.factory as dp_contents_factory

from src.definitions import Constants, Status, IMDException, DiscListContents, DisplayStrings
from src.generator.base import VirtualGenerator



class GeneratorV2(VirtualGenerator):

    def generate_datapack(self, entry_list: DiscListContents, user_settings={}):

        #read settings
        pack_format = user_settings.get('version').get('dp', Constants.DEFAULT_PACK_FORMAT)
        offset = user_settings.get('offset', 0)

        for i,entry in enumerate(entry_list.entries):
            entry.custom_model_data = i + offset + 1

        datapack_name = user_settings.get('name', Constants.DEFAULT_PACK_NAME)
        datapack_name = datapack_name + Constants.DATAPACK_SUFFIX

        #read datapack contents
        dp = dp_contents_factory.get(pack_format)

        #following variables are not explicitly used, but are included in locals()
        #  which gets used to format template strings from contents.datapack
        dp_version_str = dp.version_str
        dp_num_discs = len(entry_list.entries)
        mix_mono_title = DisplayStrings.STR_MIXMONO_TITLE

        #write datapack
        try:
            self.delete_pack(datapack_name)
            os.makedirs(datapack_name)

            with self.set_directory(datapack_name):
                #write 'creeper.json'
                #generate JSON for music disc entries, then reach into dict and add them
                #  to the drop pool manually
                creeper_music_entries = []
                creeper_music_entries.append(dp.get_creeper_music_entry_base())

                for entry in entry_list.entries:
                    creeper_music_entries.append(self.fmt_json(dp.get_creeper_music_entry_custom(), locals()))

                creeper_json = dp.get_creeper_json(creeper_music_entries)
                self.write_single(creeper_json, locals())

                #write other datapack files
                for dp_file in dp.contents:
                    if dp_file['repeat'] == 'single':
                        self.write_single(dp_file, locals())
                    elif dp_file['repeat'] == 'copy':
                        self.write_copy(dp_file, entry_list, locals())
                    elif dp_file['repeat'] == 'copy_within':
                        self.write_copy_within(dp_file, entry_list, locals())

        except UnicodeEncodeError:
            raise IMDException(Status.BAD_UNICODE_CHAR)

        except FileExistsError:
            raise IMDException(Status.PACK_DIR_IN_USE)

        #copy pack.png
        self.copy_pack_png(datapack_name, user_settings)

        #move pack to .zip, if selected
        use_zip = user_settings.get('zip', False)

        if use_zip:
            self.zip_pack(datapack_name)



    def generate_resourcepack(self, entry_list: DiscListContents, user_settings={}):

        #read settings
        pack_format = user_settings.get('version').get('rp', Constants.DEFAULT_PACK_FORMAT)
        offset = user_settings.get('offset', 0)

        for i,entry in enumerate(entry_list.entries):
            entry.custom_model_data = i + offset + 1

        resourcepack_name = user_settings.get('name', Constants.DEFAULT_PACK_NAME)
        resourcepack_name = resourcepack_name + Constants.RESOURCEPACK_SUFFIX

        #write resourcepack
        try:
            self.delete_pack(resourcepack_name)
            os.makedirs(resourcepack_name)

            #write resourcepack files to pack directory
            with self.set_directory(resourcepack_name):
                self.write_rp_framework(entry_list, pack_format)
                self.write_item_models(entry_list)
                self.copy_assets(entry_list)

        except UnicodeEncodeError:
            raise IMDException(Status.BAD_UNICODE_CHAR)

        except FileExistsError:
            raise IMDException(Status.PACK_DIR_IN_USE)

        #copy pack.png
        self.copy_pack_png(resourcepack_name, user_settings)

        #move pack to .zip, if selected
        use_zip = user_settings.get('zip', False)

        if use_zip:
            self.zip_pack(resourcepack_name)

    # generate directory structure and framework files
    def write_rp_framework(self, entry_list: DiscListContents, pack_format: int):

        #build resourcepack directory tree
        os.makedirs(os.path.join('assets', 'minecraft', 'atlases'))
        os.makedirs(os.path.join('assets', 'minecraft', 'models', 'item'))
        os.makedirs(os.path.join('assets', 'minecraft', 'sounds', 'records'))
        os.makedirs(os.path.join('assets', 'minecraft', 'textures', 'item'))

        #write 'pack.mcmeta'
        with open(os.path.join('pack.mcmeta'), 'w', encoding='utf-8') as pack:
            pack_mcmeta_json = {
                'pack':{
                    'pack_format':pack_format,
                    'description':(Constants.RESOURCEPACK_DESC % len(entry_list.internal_names))
                }
            }

            json.dump(pack_mcmeta_json, pack, indent=4)

        #write 'sounds.json'
        with self.set_directory(os.path.join('assets', 'minecraft')):
            with open('sounds.json', 'w', encoding='utf-8') as sounds:
                sounds_json = {}

                for name in entry_list.internal_names:
                    sound = {
                        'sounds':[{
                            'name':f'records/{name}',
                            'stream':True
                        }]
                    }

                    sounds_json[f'music_disc.{name}'] = sound

                json.dump(sounds_json, sounds, indent=4)

        #write items atlas
        with self.set_directory(os.path.join('assets', 'minecraft', 'atlases')):
            with open('blocks.json', 'w', encoding='utf-8') as blocks:
                atlas_json = {
                    "sources": [
                        {
                            "type": "directory",
                            "source": "item",
                            "prefix": "item/"
                        }
                    ]
                }

                json.dump(atlas_json, blocks, indent=4)

    # generate item models
    def write_item_models(self, entry_list: DiscListContents):

        with self.set_directory(os.path.join('assets', 'minecraft', 'models', 'item')):

            #write 'music_disc_11.json'
            with open('music_disc_11.json', 'w', encoding='utf-8') as music_disc_11:

                override_list = []
                for entry in entry_list.entries:

                    override_list.append({
                        'predicate': {'custom_model_data': entry.custom_model_data},
                        'model': f'item/music_disc_{entry.internal_name}'
                    })

                music_disc_11_json = {
                    'parent': 'item/generated',
                    'textures': {'layer0': 'item/music_disc_11'},
                    'overrides': override_list
                }

                json.dump(music_disc_11_json, music_disc_11, indent=4)

            #write 'music_disc_*.json' files
            for name in entry_list.internal_names:
                with open(f'music_disc_{name}.json', 'w', encoding='utf-8') as music_disc:

                    music_disc_json = {
                        'parent':'item/generated',
                        'textures':{'layer0': f'item/music_disc_{name}'}
                    }

                    json.dump(music_disc_json, music_disc, indent=4)

    # generate assets dir
    def copy_assets(self, entry_list: DiscListContents):

        #copy sound and texture files
        for entry in entry_list.entries:
            with self.set_directory(os.path.join('assets', 'minecraft', 'sounds', 'records')):
                shutil.copyfile(entry.track_file, f'{entry.internal_name}.ogg')

            with self.set_directory(os.path.join('assets', 'minecraft', 'textures', 'item')):
                shutil.copyfile(entry.texture_file, f'music_disc_{entry.internal_name}.png')



    def copy_pack_png(self, pack_name: str, user_settings: dict):
        try:
            if 'pack' in user_settings:
                shutil.copyfile(user_settings['pack'], os.path.join(pack_name, 'pack.png'))
            else:
                raise FileNotFoundError

        except (FileNotFoundError, IOError):
            print("Warning: No pack.png found. Your datapack/resourcepack will not have an icon.")

    def delete_pack(self, pack_name):
        #try to remove old pack. If pack folder exists but mcmeta does not,
        #  then this directory may belong to something else so don't delete
        if os.path.isdir(pack_name):
            if not os.path.isfile(os.path.join(pack_name, 'pack.mcmeta')):
                raise FileExistsError
            else:
                shutil.rmtree(pack_name, ignore_errors=True)

    def zip_pack(self, pack_name: str):
        pack_name_zip = pack_name + Constants.ZIP_SUFFIX

        try:
            #remove old zip
            if os.path.exists(pack_name_zip):
                os.remove(pack_name_zip)

            #generate new zip archive
            with zipfile.ZipFile(pack_name_zip, 'w') as rp_zip:
                for root, dirs, files in os.walk(pack_name):
                    root_zip = os.path.relpath(root, pack_name)

                    for file in files:
                        rp_zip.write(os.path.join(root, file), os.path.join(root_zip, file))

            #remove pack folder
            if os.path.exists(pack_name_zip):
                shutil.rmtree(pack_name, ignore_errors=True)

        except (OSError, zipfile.BadZipFile):
            #remove bad zip, if it exists
            if os.path.exists(pack_name_zip):
                os.remove(pack_name_zip)

            # raise exception to alert user
            raise IMDException(Status.BAD_ZIP)

    # apply string formatting to the given string
    # use ** to expand fmt_dict into kwargs for formatting
    def fmt_str(self, str: str, fmt_dict):
        return str.format(**fmt_dict)
    
    # apply string formatting, but cast the result to int
    # useful for pack_format, setting minecraft:custom_model_data, etc.
    def fmt_int(self, int_str: str, fmt_dict):
        return int(self.fmt_str(int_str, fmt_dict))

    # recursively apply string formatting to any string-type
    #   value in the given json dict or json sub-list
    def fmt_json(self, obj: Union[dict, list], fmt_dict):

        #change iterator depending on type, so that the iterated
        #  object's contents can always be accessed by obj[k]
        #dict: obj[key of element]
        #list: obj[index of element]
        if type(obj) == list:
            iterator = [i for i in range(len(obj))]
            fmt_obj = list(obj)
        else:
            iterator = [k for k in obj]
            fmt_obj = dict(obj)

        for k in iterator:

            # object is a string - format
            if type(obj[k]) == str:
                # integer encoded as formatted string
                if '(int){' in obj[k]:
                    int_obj = obj[k].replace('(int){', '{')
                    fmt_obj[k] = self.fmt_int(int_obj, fmt_dict)

                # true string
                else:
                    fmt_obj[k] = self.fmt_str(obj[k], fmt_dict)

            # object is a list or dict - continue recursing
            elif type(obj[k]) in [dict, list]:
                fmt_obj[k] = self.fmt_json(obj[k], fmt_dict)

        return fmt_obj

    # apply string formatting to each element of the given
    #   list and combine them into a single path string.
    # use * to splat fmt_path into multiple strings
    #   for os.path.join
    def fmt_path(self, path: list, fmt_dict) -> str:
        fmt_path = [self.fmt_str(p, fmt_dict) for p in path]
        return os.path.join(*fmt_path)



    # write a single copy of a file based on a reference
    #  object from contents.datapack
    def write_single(self, src: dict, fmt_dict):
        fmt_dict.update(locals())
        f_dst = self.fmt_path(src['path'], fmt_dict)
        d_dst = os.path.dirname(f_dst)

        if not d_dst == '' and not os.path.exists(d_dst):
            os.makedirs(d_dst)

        with open(f_dst, 'w', encoding='utf-8') as dst:
            self.write_pack_file(src, dst, fmt_dict)

    # write several copies of a file, one copy per
    #   entry in entry_list
    def write_copy(self, src: dict, entry_list: DiscListContents, fmt_dict):
        for entry in entry_list.entries:
            fmt_dict.update(locals())
            f_dst = self.fmt_path(src['path'], fmt_dict)
            d_dst = os.path.dirname(f_dst)

            if not os.path.exists(d_dst):
                os.makedirs(d_dst)

            with open(f_dst, 'w', encoding='utf-8') as dst:
                self.write_pack_file(src, dst, fmt_dict)

    # write the same lines into a file multiple times,
    #   once per entry in entry_list
    def write_copy_within(self, src: dict, entry_list: DiscListContents, fmt_dict):
        f_dst = self.fmt_path(src['path'], fmt_dict)
        d_dst = os.path.dirname(f_dst)

        if not os.path.exists(d_dst):
            os.makedirs(d_dst)

        with open(f_dst, 'w', encoding='utf-8') as dst:
            for entry in entry_list.entries:
                fmt_dict.update(locals())

                self.write_pack_file(src, dst, fmt_dict)

    # given a reference dict, detect whether it will
    #   write a plaintext or JSON file
    def write_pack_file(self, src: dict, dst: TextIO, fmt_dict):
        if type(src['contents']) == str:
            self.write_text_file(src, dst, fmt_dict)

        elif type(src['contents']) == dict:
            self.write_json_file(src, dst, fmt_dict)

    # write a plaintext file, optionally formatting
    #   the given string
    def write_text_file(self, src: dict, dst: TextIO, fmt_dict):
        if src.get('format_contents', True):
            dst.writelines(self.fmt_str(src['contents'].lstrip(), fmt_dict))
        else:
            dst.writelines(src['contents'].lstrip())

    # write a JSON file, optionally applying recursive
    #   string formatting to every string value in the
    #   given dict
    def write_json_file(self, src: dict, dst: TextIO, fmt_dict):
        if src.get('format_contents', True):
            json.dump(self.fmt_json(src['contents'], fmt_dict), dst, indent=4)
        else:
            json.dump(src['contents'], dst, indent=4)


