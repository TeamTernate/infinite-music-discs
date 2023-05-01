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

from src.contents.datapack import file_list as dp_file_list
from src.definitions import Constants, Helpers, Status, DiscListContents
from src.generator.base import VirtualGenerator



class GeneratorV2(VirtualGenerator):

    #TODO: what happens when command syntax changes? Can't be backwards compatible
    #  and copy from reference files... different sets of reference files?
    #  command-to-string generation engine? too complex to maintain?
    def generate_datapack(self, entry_list: DiscListContents, user_settings={}):

        #read settings
        pack_format = user_settings.get('version').get('dp', Constants.DEFAULT_PACK_FORMAT)
        offset = user_settings.get('offset', 0)

        for i,entry in enumerate(entry_list.entries):
            entry.custom_model_data = i + offset + 1

        datapack_name = user_settings.get('name', Constants.DEFAULT_PACK_NAME)
        datapack_name = datapack_name + Constants.DATAPACK_SUFFIX

        dp_version_str = f'v{self._version_major}.{self._version_minor}'

        #write datapack
        try:
            self.write_dp_framework(entry_list, datapack_name, pack_format)

            for dp_file in dp_file_list:
                if dp_file['repeat'] == 'single':
                    self.write_single(dp_file, locals())
                elif dp_file['repeat'] == 'copy':
                    self.write_copy(dp_file, entry_list, locals())
                elif dp_file['repeat'] == 'copy_within':
                    self.write_copy_within(dp_file, entry_list, locals())

            self.write_creeper_loottable(datapack_name, entry_list)

        except UnicodeEncodeError:
            return Status.BAD_UNICODE_CHAR

        except FileExistsError:
            return Status.PACK_DIR_IN_USE

        #copy pack.png
        try:
            if 'pack' in user_settings:
                shutil.copyfile(user_settings['pack'], os.path.join(datapack_name, 'pack.png'))
            else:
                raise FileNotFoundError

        except (FileNotFoundError, IOError):
            print("Warning: No pack.png found. Your datapack will not have an icon.")

        #move pack to .zip, if selected
        use_zip = user_settings.get('zip', False)

        if use_zip:
            zip_status = self.zip_pack(datapack_name)

            if(zip_status != Status.SUCCESS):
                print("Error: Failed to zip datapack. Datapack has been generated as folder instead.")
                return zip_status

        return Status.SUCCESS

    # generate directory structure and framework files
    #TODO: move inside dp immediately so there's no risk of breaking external stuff
    def write_dp_framework(self, entry_list: DiscListContents, datapack_name: str, pack_format: int):

        #try to remove old datapack. If datapack folder exists but mcmeta does not,
        #  then this directory may belong to something else so don't delete
        if os.path.isdir(datapack_name):
            if not os.path.isfile(os.path.join(datapack_name, 'pack.mcmeta')):
                raise FileExistsError
            else:
                shutil.rmtree(datapack_name, ignore_errors=True)

        #build datapack directory tree
        os.makedirs(os.path.join(datapack_name, 'data', 'minecraft', 'tags', 'functions'))
        os.makedirs(os.path.join(datapack_name, 'data', 'minecraft', 'loot_tables', 'entities'))
        os.makedirs(os.path.join(datapack_name, 'data', datapack_name, 'functions'))
        os.makedirs(os.path.join(datapack_name, 'data', datapack_name, 'advancements'))

        #write 'pack.mcmeta'
        with open(os.path.join(datapack_name, 'pack.mcmeta'), 'w', encoding='utf-8') as pack:
            pack.write(json.dumps({
                'pack': {
                    'pack_format': pack_format,
                    'description': (Constants.DATAPACK_DESC % len(entry_list.internal_names))
                }
            }, indent=4))

    # generate creeper loottable
    def write_creeper_loottable(self, datapack_name: str, entry_list: DiscListContents):

        dp_base = os.getcwd()
        dp_dir = os.path.join(dp_base, datapack_name, 'data', 'minecraft', 'loot_tables', 'entities')

        creeper_mdentries = []
        creeper_mdentries.append({'type':'minecraft:tag', 'weight':1, 'name':'minecraft:creeper_drop_music_discs', 'expand':True})

        for entry in entry_list.entries:
            creeper_mdentries.append({
                'type':'minecraft:item',
                'weight':1,
                'name':'minecraft:music_disc_11',
                'functions':[{
                    'function':'minecraft:set_nbt',
                    'tag':f'{{CustomModelData:{entry.custom_model_data}, HideFlags:32, display:{{Lore:[\"\\\"\\\\u00a77{entry.title}\\\"\"]}}}}'
                }]
            })

        creeper_normentries = [{
            'type':'minecraft:item',
            'functions':[{
                    'function':'minecraft:set_count',
                    'count':{'min':0.0, 'max':2.0, 'type':'minecraft:uniform'}
                }, {
                    'function':'minecraft:looting_enchant',
                    'count':{'min':0.0, 'max':1.0}
                }],
            'name':'minecraft:gunpowder'
        }]

        creeper_json = {
            'type':'minecraft:entity',
            'pools':[
                {'rolls':1, 'entries':creeper_normentries},
                {'rolls':1, 'entries':creeper_mdentries, 'conditions':[{
                    'condition':'minecraft:entity_properties',
                    'predicate':{'type':'#minecraft:skeletons'},
                    'entity':'killer'
                }]
            }]
        }

        #write 'creeper.json'
        with open(os.path.join(dp_dir, 'creeper.json'), 'w', encoding='utf-8') as creeper:
            creeper.write(json.dumps(creeper_json, indent=4))



    def generate_resourcepack(self, entry_list: DiscListContents, user_settings={}, cleanup_tmp: bool = True):

        #read settings
        pack_format = user_settings.get('version').get('rp', Constants.DEFAULT_PACK_FORMAT)
        offset = user_settings.get('offset', 0)

        resourcepack_name = user_settings.get('name', Constants.DEFAULT_PACK_NAME)
        resourcepack_name = resourcepack_name + Constants.RESOURCEPACK_SUFFIX

        #capture base dir
        base_dir = os.getcwd()

        #write resourcepack
        #use chdir to move around directory structure and reduce file paths
        try:
            self.write_rp_framework(entry_list, resourcepack_name, pack_format)

            os.chdir(os.path.join(base_dir, resourcepack_name, 'assets', 'minecraft', 'models', 'item'))
            self.write_item_models(entry_list, offset)

            os.chdir(os.path.join(base_dir, resourcepack_name, 'assets', 'minecraft'))
            self.copy_assets(entry_list)

        except UnicodeEncodeError:
            return Status.BAD_UNICODE_CHAR
        
        except FileExistsError:
            return Status.PACK_DIR_IN_USE
        
        finally:
            os.chdir(base_dir)

        #copy pack.png
        try:
            if 'pack' in user_settings:
                shutil.copyfile(user_settings['pack'], os.path.join(resourcepack_name, 'pack.png'))
            else:
                raise FileNotFoundError

        except (FileNotFoundError, IOError):
            print("Warning: No pack.png found. Your resourcepack will not have an icon.")

        #move pack to .zip, if selected
        use_zip = user_settings.get('zip', False)

        if use_zip:
            zip_status = self.zip_pack(resourcepack_name)

            if(zip_status != Status.SUCCESS):
                print("Error: Failed to zip resourcepack. Resourcepack has been generated as folder instead.")
                return zip_status

        #cleanup temp work directory
        if cleanup_tmp:
            shutil.rmtree(self.tmp_path, ignore_errors=True)
            self.tmp_path = None

        return Status.SUCCESS

    # generate directory structure and framework files
    def write_rp_framework(self, entry_list: DiscListContents, resourcepack_name: str, pack_format: int):

        #try to remove old resourcepack. If resourcepack folder exists but mcmeta does not,
        #  then this directory may belong to something else so don't delete
        if os.path.isdir(resourcepack_name):
            if not os.path.isfile(os.path.join(resourcepack_name, 'pack.mcmeta')):
                raise FileExistsError
            else:
                shutil.rmtree(resourcepack_name, ignore_errors=True)

        #build resourcepack directory tree
        os.makedirs(os.path.join(resourcepack_name, 'assets', 'minecraft', 'models', 'item'))
        os.makedirs(os.path.join(resourcepack_name, 'assets', 'minecraft', 'sounds', 'records'))
        os.makedirs(os.path.join(resourcepack_name, 'assets', 'minecraft', 'textures', 'item'))

        #write 'pack.mcmeta'
        with open(os.path.join(resourcepack_name, 'pack.mcmeta'), 'w', encoding='utf-8') as pack:
            pack.write(json.dumps({
                'pack':{
                    'pack_format':pack_format,
                    'description':(Constants.RESOURCEPACK_DESC % len(entry_list.internal_names))
                }
            }, indent=4))

        #write 'sounds.json'
        with open(os.path.join(resourcepack_name, 'assets', 'minecraft', 'sounds.json'), 'w', encoding='utf-8') as sounds:
            json_dict = {}

            for name in entry_list.internal_names:
                sound = {
                    'sounds':[{
                        'name':f'records/{name}',
                        'stream':True
                    }]
                }

                json_dict[f'music_disc.{name}'] = sound

            sounds.write(json.dumps(json_dict, indent=4))

    # generate item models
    def write_item_models(self, entry_list: DiscListContents, offset: int):

        #write 'music_disc_11.json'
        with open('music_disc_11.json', 'w', encoding='utf-8') as music_disc_11:
            json_list = []
            for i, name in enumerate(entry_list.internal_names):
                j = i + offset + 1

                json_list.append({
                    'predicate':{'custom_model_data':j},
                    'model':f'item/music_disc_{name}'
                })

            music_disc_11.write(json.dumps({
                'parent':'item/generated',
                'textures':{'layer0': 'item/music_disc_11'},
                'overrides':json_list
            }, indent=4))

        #write 'music_disc_*.json' files
        for name in entry_list.internal_names:
            with open(f'music_disc_{name}.json', 'w', encoding='utf-8') as music_disc:
                music_disc.write(json.dumps({
                    'parent':'item/generated',
                    'textures':{'layer0': f'item/music_disc_{name}'}
                }, indent=4))

    # generate assets dir
    def copy_assets(self, entry_list: DiscListContents):

        #copy sound and texture files
        for entry in entry_list.entries:
            shutil.copyfile(entry.track_file, os.path.join('sounds', 'records', f'{entry.internal_name}.ogg'))
            shutil.copyfile(entry.texture_file, os.path.join('textures', 'item', f'music_disc_{entry.internal_name}.png'))



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

            return Status.BAD_ZIP
        
        return Status.SUCCESS

    # helper function that copies the contents of f_src into f_dst, while applying
    #   string formatting to every line
    # if called with fmt_dict=locals(), it will effectively format each line of
    #   f_src like an f-string, with all the variables in the caller's scope
    def copy_func_with_fmt(self, f_src: str, f_dst: str, fmt_dict):
        with open(f_src, 'r', encoding='utf-8') as src:
            with open(f_dst, 'w', encoding='utf-8') as dst:

                for line in src.readlines():

                    #decompose fmt_dict into its key-value pairs so
                    #  it can be used for string formatting
                    line_fmt = line.format(**fmt_dict)
                    dst.write(line_fmt)

    # helper function that copes the contents of f_src into f_dst once per
    #   disc. Also applies string formatting to every line
    #
    # if called with fmt_dict=locals(), it will effectively format each line of
    #   f_src like an f-string, with all the variables in the caller's scope.
    #   "entry" is explicitly included in the formatting since it didn't exist
    #   in the caller's scope
    def copy_lines_to_func_with_fmt(self, f_src: str, f_dst: str, entry_list: DiscListContents, fmt_dict):
        with open(f_src, 'r', encoding='utf-8') as src:
            with open(f_dst, 'w', encoding='utf-8') as dst:

                #return to the top of f_src with every disc to reread the same contents
                #more efficient than reopening the file every time
                for entry in entry_list.entries:
                    src.seek(0)
                    for line in src.readlines():

                        #decompose fmt_dict into its key-value pairs so
                        #  it can be used for string formatting
                        line_fmt = line.format(**fmt_dict, entry=entry)
                        dst.write(line_fmt)

    # recursively apply string formatting to any string-type
    #   value in the given json dict or json sub-list
    def fmt_json(self, json: Union[dict, list], fmt_dict):

        #change iterator depending on type, so that the iterated
        #  object's contents can always be accessed by json[k]
        #dict: json[key of element]
        #list: json[index of element]
        if type(json) == list:
            iterator = [i for i in range(len(json))]
        else:
            iterator = [k for k in json]

        for k in iterator:

            if type(json[k]) == str:
                json[k] = json[k].format(**fmt_dict)

            elif type(json[k]) in [dict, list]:
                json[k] = self.fmt_json(json[k], fmt_dict)

        return json

    # apply string formatting to each element of the given
    #   list and combine them into a single path string.
    # use ** to expand fmt_dict into kwargs and use *
    #   to splat fmt_path into multiple strings for
    #   os.path.join
    def fmt_path(self, path: list, fmt_dict) -> str:
        fmt_path = [p.format(**fmt_dict) for p in path]
        return os.path.join(*fmt_path)



    def write_single(self, src: dict, fmt_dict):
        fmt_dict.update(locals())
        f_dst = self.fmt_path(src['path'], fmt_dict)
        d_dst = os.path.dirname(f_dst)

        if not os.path.exists(d_dst):
            os.makedirs(d_dst)

        with open(f_dst, 'w', encoding='utf-8') as dst:
            self.write_pack_file(src, dst, fmt_dict)

    def write_copy(self, src: dict, entry_list: DiscListContents, fmt_dict):
        for entry in entry_list.entries:
            fmt_dict.update(locals())
            f_dst = self.fmt_path(src['path'], fmt_dict)
            d_dst = os.path.dirname(f_dst)

            if not os.path.exists(d_dst):
                os.makedirs(d_dst)

            with open(f_dst, 'w', encoding='utf-8') as dst:
                self.write_pack_file(src, dst, fmt_dict)

    def write_copy_within(self, src: dict, entry_list: DiscListContents, fmt_dict):
        f_dst = self.fmt_path(src['path'], fmt_dict)
        d_dst = os.path.dirname(f_dst)

        if not os.path.exists(d_dst):
            os.makedirs(d_dst)

        with open(f_dst, 'w', encoding='utf-8') as dst:
            for entry in entry_list.entries:
                fmt_dict.update(locals())

                self.write_pack_file(src, dst, fmt_dict)

    def write_pack_file(self, src: dict, dst: TextIO, fmt_dict):
        if type(src['contents']) == str:
            dst.writelines(src['contents'].lstrip().format(**fmt_dict))

        elif type(src['contents']) == dict:
            json.dump(self.fmt_json(src['contents'], fmt_dict), dst, indent=4)

    # helper function that copies the contents of f_src into f_dst, while applying
    #   string formatting to every string-type value in the given json file
    # if called with fmt_dict=locals(), it will effectively format each line of
    #   f_src like an f-string, with all the variables in the caller's scope
    def copy_json_with_fmt(self, f_src: str, f_dst: str, fmt_dict):
        with open(f_src, 'r', encoding='utf-8') as src:
            with open(f_dst, 'w', encoding='utf-8') as dst:

                src_fmt = json.load(src)
                src_fmt = self.fmt_json(src_fmt, fmt_dict)
                dst.write(json.dumps(src_fmt, indent=4))


