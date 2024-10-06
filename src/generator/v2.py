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

from src.contents.datapack.factory import AbstractDatapackFactory
from src.contents.resourcepack.factory import AbstractResourcepackFactory

from src.definitions import Constants, Status, IMDException, DiscListContents, DisplayStrings
from src.generator.base import VirtualGenerator



class GeneratorV2(VirtualGenerator):

    def generate_datapack(self, entry_list: DiscListContents, user_settings={}):

        #read settings
        pack_format = user_settings.get('version').get('dp', Constants.DEFAULT_PACK_FORMAT)
        offset = user_settings.get('offset', 0)

        for i,entry in enumerate(entry_list.entries):
            entry.custom_model_data = i + offset + 1

        pack_name = user_settings.get('name', Constants.DEFAULT_PACK_NAME)
        datapack_name = pack_name + Constants.DATAPACK_SUFFIX

        #read datapack contents
        dp = AbstractDatapackFactory().get(pack_format)

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

        pack_name = user_settings.get('name', Constants.DEFAULT_PACK_NAME)
        resourcepack_name = pack_name + Constants.RESOURCEPACK_SUFFIX

        #read pack contents
        rp = AbstractResourcepackFactory().get(pack_format)

        #following variables are not explicitly used, but are included in locals()
        #  which gets used to format template strings from contents.resourcepack
        rp_num_discs = len(entry_list.entries)

        #write resourcepack
        try:
            self.delete_pack(resourcepack_name)
            os.makedirs(resourcepack_name)

            #write resourcepack files to pack directory
            with self.set_directory(resourcepack_name):
                # write 'sounds.json'
                sounds_json_entries = {}

                for entry in entry_list.entries:
                    sounds_json_entries.update(self.fmt_json(rp.get_sounds_json_entry(), locals()))

                sounds_json = rp.get_sounds_json(sounds_json_entries)
                self.write_single(sounds_json, locals())

                # write 'music_disc_11.json'
                music_disc_11_entries = []

                for entry in entry_list.entries:
                    music_disc_11_entries.append(self.fmt_json(rp.get_music_disc_11_entry(), locals()))

                music_disc_11_json = rp.get_music_disc_11_json(music_disc_11_entries)
                self.write_single(music_disc_11_json, locals())

                #write other data files
                for rp_file in rp.contents:
                    if rp_file['repeat'] == 'single':
                        self.write_single(rp_file, locals())
                    elif rp_file['repeat'] == 'copy':
                        self.write_copy(rp_file, entry_list, locals())
                    elif rp_file['repeat'] == 'copy_within':
                        self.write_copy_within(rp_file, entry_list, locals())

                #copy assets
                sound_path = self.fmt_path(rp.get_sound_path(), locals())
                texture_path = self.fmt_path(rp.get_texture_path(), locals())

                os.makedirs(sound_path)
                os.makedirs(texture_path)

                for entry in entry_list.entries:
                    with self.set_directory(sound_path):
                        shutil.copyfile(entry.track_file, f'{entry.internal_name}.ogg')

                    with self.set_directory(texture_path):
                        shutil.copyfile(entry.texture_file, f'music_disc_{entry.internal_name}.png')

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
    
    # apply string formatting, but cast the result to float
    # used for the data-driven jukebox "length_in_seconds"
    def fmt_float(self, flt_str: str, fmt_dict):
        return float(self.fmt_str(flt_str, fmt_dict))

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

                # float encoded as formatted string
                elif '(float){' in obj[k]:
                    flt_obj = obj[k].replace('(float){', '{')
                    fmt_obj[k] = self.fmt_float(flt_obj, fmt_dict)

                # true string
                else:
                    fmt_obj[k] = self.fmt_str(obj[k], fmt_dict)

            # object is a list or dict - continue recursing
            elif type(obj[k]) in [dict, list]:
                fmt_obj[k] = self.fmt_json(obj[k], fmt_dict)

            # finally, format key and replace old key with new, formatted key
            if type(k) == str:
                fmt_k = self.fmt_str(k, fmt_dict)
                fmt_obj[fmt_k] = fmt_obj.pop(k)

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


