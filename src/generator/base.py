# -*- coding: utf-8 -*-
#
#Infinite Music Discs generator module base class
#Generation tool, datapack design, and resourcepack design by link2_thepast

import os
import shutil
import pyffmpeg
import tempfile
import multiprocessing

from math import ceil
from typing import Callable

from contextlib import contextmanager
from mutagen import MutagenError
from mutagen.mp3 import MP3, HeaderNotFoundError
from mutagen.oggvorbis import OggVorbis
from src.definitions import Status, IMDException, DiscListContents, DiscListEntryContents, MpTaskContents



class VirtualGenerator():
    def __init__(self):
        self.tmp_path = None

    def validate(self, entry_list: DiscListContents, settings={}):
        packpng = settings.get('pack', '')

        #lists are not empty
        if(len(entry_list) == 0):
            raise IMDException(Status.LIST_EMPTY)

        #internal names are all unique
        if( len(entry_list.internal_names) > len(set(entry_list.internal_names)) ):
            raise IMDException(Status.DUP_INTERNAL_NAME)

        for e in entry_list.entries:
            #image is provided
            if(e.texture_file == ''):
                raise IMDException(Status.IMAGE_FILE_NOT_GIVEN)

            #image files still exist
            if(not os.path.isfile(e.texture_file)):
                raise IMDException(Status.IMAGE_FILE_MISSING)

            #images are all .png
            if(not ( '.png' in e.texture_file )):
                raise IMDException(Status.BAD_IMAGE_TYPE)

            #track is provided
            if(e.track_file == ''):
                raise IMDException(Status.TRACK_FILE_NOT_GIVEN)

            #track files still exist
            if(not os.path.isfile(e.track_file)):
                raise IMDException(Status.TRACK_FILE_MISSING)

            #tracks are all .mp3, .wav, .ogg
            if(not ( '.mp3' in e.track_file or '.wav' in e.track_file or '.ogg' in e.track_file )):
                raise IMDException(Status.BAD_TRACK_TYPE)

            #internal names are not empty
            if(e.internal_name == ''):
                raise IMDException(Status.BAD_INTERNAL_NAME)

            #internal names are letters-only
            if(not e.internal_name.isalpha()):
                raise IMDException(Status.BAD_INTERNAL_NAME)

            #internal names are all lowercase
            if(not e.internal_name.islower()):
                raise IMDException(Status.BAD_INTERNAL_NAME)

        #if pack icon is provided
        if(not packpng == ''):
            #image file still exists
            if(not os.path.isfile(packpng)):
                raise IMDException(Status.PACK_IMAGE_MISSING)

            #image is .png
            if(not ('.png' in packpng)):
                raise IMDException(Status.BAD_PACK_IMAGE_TYPE)



    def create_tmp(self):
        if self.tmp_path != None:
            shutil.rmtree(self.tmp_path)

        self.tmp_path = tempfile.mkdtemp()

    def cleanup_tmp(self):
        if self.tmp_path != None:
            shutil.rmtree(self.tmp_path, ignore_errors=True)
            self.tmp_path = None



    def convert_all_to_ogg(self, entry_list: DiscListContents, settings: dict, convert_cb: Callable):
        args: list[MpTaskContents] = []

        # pre-prepare paths to reduce work and data transfer in
        #   child threads
        for e in entry_list.entries:
            arg = self.prepare_for_convert(e, settings)
            args.append(arg)

        # use multiprocessing to run FFmpeg over many files in parallel, if the user desires
        if(settings.get('par_proc', False)):
            cpus = multiprocessing.cpu_count()

            with multiprocessing.Pool(processes=cpus) as pool:
                result = pool.imap_unordered(self.convert_to_ogg, args)

                # imap_unordered yields every time a task finishes; by iterating
                #   over the returned iterable like this we can cause
                #   cb_update to run after each task finishes. Only works
                #   with imap, not map or starmap
                for r in result:
                    convert_cb()

        # otherwise, by default, run them one-by-one (multiprocessing doesn't work for
        #   everyone and it's better to opt-in to an experimental feature than for the app
        #   to break by default)
        else:
            for a in args:
                self.convert_to_ogg(a)
                convert_cb()

        # update entry list to point to converted files
        for (a, e) in zip(args, entry_list.entries):
            e.track_file = a.out_track



    def prepare_for_convert(self, track_entry: DiscListEntryContents, settings: dict):
        track = track_entry.track_file
        internal_name = track_entry.internal_name

        # build FFmpeg args from settings
        args = ''

        if settings.get('mix_mono', False):
            args += ' -ac 1'

        # detect whether ogg files should be processed
        proc_ogg = settings.get('proc_ogg', False) or settings.get('mix_mono', False)

        # prepare input file
        track_ext = track.split('/')[-1].split('.')[-1]
        tmp_track = os.path.join(self.tmp_path, internal_name + '.tmp.' + track_ext)
        shutil.copyfile(track, tmp_track)

        #strip any ID3 metadata from mp3
        if '.mp3' in tmp_track:
            try:
                meta_mp3 = MP3(tmp_track)
                meta_mp3.delete()
                meta_mp3.save()
            except HeaderNotFoundError:
                #no metadata to be removed, ignore
                pass

        #exit if metadata removal failed
        if not os.path.isfile(tmp_track):
            raise IMDException(Status.BAD_MP3_META)

        # prepare output file location
        out_name = internal_name + '.ogg'
        out_track = os.path.join(self.tmp_path, out_name)

        return MpTaskContents(args, proc_ogg, track, tmp_track, out_track)



    def convert_to_ogg(self, data: MpTaskContents):

        #create FFmpeg reference
        #TODO: once you update to a new version that's not broken, make sure to
        #  add 'enable_log=False' to this constructor
        ffmpeg = pyffmpeg.FFmpeg()

        # decide whether to convert or copy ogg source files
        # copy by default, since FFmpeg sometimes fails to convert files,
        #   and that causes pack generation to fail. Copying is more likely
        #   to work
        if(not data.proc_ogg and ".ogg" in data.tmp_track):
            shutil.copyfile(data.tmp_track, data.out_track)
            return

        #convert file
        try:
            ffmpeg.options(f"-nostdin -y -i {data.tmp_track} -c:a libvorbis{data.args} {data.out_track}")

        except Exception as e:
            print(e)
            raise IMDException(Status.FFMPEG_CONVERT_FAIL)

        #FIXME: uniquify exceptions
        #exit if file was not converted successfully
        if not os.path.isfile(data.out_track):
            raise IMDException(Status.BAD_OGG_CONVERT)

        if os.path.getsize(data.out_track) == 0:
            raise IMDException(Status.BAD_OGG_CONVERT)



    # context manager to simplify moving around the directory
    #   structure while generating packs. Automatically chdir's
    #   to the original directory upon exit
    @contextmanager
    def set_directory(self, path: str):
        orig_dir = os.getcwd()
        try:
            os.chdir(path)
            yield

        finally:
            os.chdir(orig_dir)

    # detect track length so that the datapack can indicate that
    #   a disc is done playing. Because IMD overrides disc "11"
    #   we need custom logic to tell Minecraft the true length
    #   of a playing disc. Otherwise it would assume IMD discs
    #   are all the same length as "11"
    # Returns disc length in seconds
    def get_track_length(self, track_entry: DiscListEntryContents):
        try:
            #capture track length in seconds
            #ffp = pyffmpeg.FFprobe(track_entry.track_file)
            #print(ffp.metadata)
            #length_s = ffp.duration
            meta_ogg = OggVorbis(track_entry.track_file)
            length_s = meta_ogg.info.length

        except FileNotFoundError:
            raise IMDException(Status.BAD_OGG_CONVERT)

        except MutagenError:
            raise IMDException(Status.BAD_OGG_META)

        return length_s

    # Convert from seconds to Minecraft ticks (20t/s)
    # Round up to avoid track getting cut off at the end
    def seconds_to_ticks(self, length: float):
        return int(ceil(length * 20.0))

    # replace quotes with a visually similar unicode character
    #   to prevent parsing errors in the final datapack
    def sanitize(self, track_entry: DiscListEntryContents):
        return track_entry.title.replace('"', '＂')

    def generate_datapack(self):
        raise NotImplementedError

    def generate_resourcepack(self):
        raise NotImplementedError


