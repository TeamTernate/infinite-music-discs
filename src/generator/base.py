# -*- coding: utf-8 -*-
#
#Infinite Music Discs generator module base class
#Generation tool, datapack design, and resourcepack design by link2_thepast

import os
import shutil
import pyffmpeg
import tempfile

from contextlib import contextmanager
from mutagen.mp3 import MP3, HeaderNotFoundError
from mutagen.oggvorbis import OggVorbis
from src.definitions import Status, IMDException, DiscListContents, DiscListEntryContents



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



    def convert_to_ogg(self, track_entry: DiscListEntryContents, settings={}, create_tmp=True, cleanup_tmp=False):
        track = track_entry.track_file
        internal_name = track_entry.internal_name
        mix_mono = settings.get('mix_mono', False)

        #FFmpeg object
        ffmpeg = pyffmpeg.FFmpeg()

        #create temp work directory
        if create_tmp:
            if self.tmp_path != None:
                shutil.rmtree(self.tmp_path)

            self.tmp_path = tempfile.mkdtemp()

        #build FFmpeg settings
        args = ''

        if mix_mono:
            args += ' -ac 1'

        #skip files that don't need to be processed
        #if args == '' and '.ogg' in track:
        #    return Status.SUCCESS, track

        #TODO: run ffmpeg on every file but use threadpools so it does all the files in parallel

        #rename file so FFmpeg can process it
        track_ext = track.split('/')[-1].split('.')[-1]
        tmp_track = os.path.join(self.tmp_path, internal_name + '.tmp.' + track_ext)

        out_name = internal_name + '.ogg'
        out_track = os.path.join(self.tmp_path, out_name)

        #copy file to temp work directory
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

        #convert file
        try:
            ffmpeg.options("-nostdin -y -i %s -c:a libvorbis%s %s" % (tmp_track, args, out_track))

        except Exception as e:
            print(e)
            raise IMDException(Status.FFMPEG_CONVERT_FAIL)

        #FIXME: uniquify exceptions
        #exit if file was not converted successfully
        if not os.path.isfile(out_track):
            raise IMDException(Status.BAD_OGG_CONVERT)

        if os.path.getsize(out_track) == 0:
            raise IMDException(Status.BAD_OGG_CONVERT)

        #usually won't clean up temp work directory here, wait until resource pack generation
        if cleanup_tmp:
            shutil.rmtree(self.tmp_path, ignore_errors=True)
            self.tmp_path = None

        return out_track



    @contextmanager
    def set_directory(self, path: str):
        orig_dir = os.getcwd()
        try:
            os.chdir(path)
            yield

        finally:
            os.chdir(orig_dir)

    def get_track_length(self, track_entry: DiscListEntryContents):
        try:
            #capture track length in seconds
            #ffp = pyffmpeg.FFprobe(track_entry.track_file)
            #print(ffp.metadata)
            #length_s = ffp.duration
            meta_ogg = OggVorbis(track_entry.track_file)
            length_s = meta_ogg.info.length

            #convert from seconds to Minecraft ticks (20 t/s)
            length_t = int(length_s) * 20

        except Exception as e:
            print(e)
            raise IMDException(Status.BAD_OGG_META)

        return length_t

    #TODO: replace quote with visually similar unicode character?
    def sanitize(self, track_entry: DiscListEntryContents):
        return track_entry.title.replace('"', '')

    def generate_datapack(self):
        raise NotImplementedError

    def generate_resourcepack(self):
        raise NotImplementedError


