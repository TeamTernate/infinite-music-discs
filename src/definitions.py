# -*- coding: utf-8 -*-
#
#Infinite Music Discs constants definition module
#Generation tool, datapack design, and resourcepack design by link2_thepast

import re
import sys
import unidecode

from enum import Enum
from datetime import datetime
from typing import List, Any
from dataclasses import dataclass, field

from PyQt5.QtGui import QColor

import build.version as version

#TODO: define some datapack strings here so they're in a known location


#constants
class Constants():
    MAX_DRAW_MULTI_DRAGDROP = 10
    STATUS_MESSAGE_ANIM_TIME_MS = 300
    STATUS_MESSAGE_SHOW_TIME_MS = 10000
    LINE_EDIT_MAX_CHARS = 100
    CUSTOM_MODEL_DATA_MAX = 16777000
    LEGACY_DP_LATEST_VERSION = 11
    FILTER_IMAGE = "Image files (*.png)"
    FILTER_MUSIC = "Music files (*.mp3 *.wav *.ogg)"

    APP_TITLE = ("IMD Datapack Generator - v%d.%d" % (version.MAJOR, version.MINOR))

    TIMESTAMP = datetime.now().strftime("%m-%d-%Y_%H%M%S")
    LOG_EXC_MSG = ""
    LOG_FILE_NAME = "imd-exception_" + TIMESTAMP + ".log"

    DEFAULT_PACK_NAME = "infinite_music_discs"
    DATAPACK_SUFFIX = '_dp'
    RESOURCEPACK_SUFFIX = '_rp'
    ZIP_SUFFIX = '.zip'

    DATAPACK_DESC = 'Adds %d custom music discs'
    RESOURCEPACK_DESC = 'Adds %d custom music discs'
    DEFAULT_PACK_FORMAT = 8     #TODO: can this come from PackFormatsDict automatically?

class Regexes():
    # QPosIntLineEdit
    LE_POS_INT = '(^[0-9]{0,8}$|^$)'

    # QAlphaLineEdit
    LE_ALPHA = '(^[a-z_]*$|^$)'



#typedefs
class ButtonType(Enum):
    IMAGE = 1
    TRACK = 2
    NEW_TRACK = 3
    ARROW_UP = 4
    ARROW_DOWN = 5
    PACKPNG = 6

class SettingType(Enum):
    PACKPNG = 1
    CHECK = 2
    RADIO = 3
    DROPDOWN = 4
    NUM_ENTRY = 5
    TXT_ENTRY = 6

class Status(Enum):
    SUCCESS = 0
    LIST_EMPTY = 1
    LIST_UNEVEN_LENGTH = 2
    IMAGE_FILE_MISSING = 3
    BAD_IMAGE_TYPE = 4
    TRACK_FILE_MISSING = 5
    BAD_TRACK_TYPE = 6
    BAD_INTERNAL_NAME = 7
    PACK_IMAGE_MISSING = 8
    BAD_PACK_IMAGE_TYPE = 9
    BAD_OGG_CONVERT = 10
    BAD_ZIP = 11
    IMAGE_FILE_NOT_GIVEN = 12
    TRACK_FILE_NOT_GIVEN = 13
    BAD_MP3_META = 14
    BAD_UNICODE_CHAR = 15
    FFMPEG_CONVERT_FAIL = 16
    DUP_INTERNAL_NAME = 17
    BAD_OGG_META = 18

class FileExt():
    PNG = 'png'
    MP3 = 'mp3'
    WAV = 'wav'
    OGG = 'ogg'
    TXT = 'txt'

class SupportedFormats():
    TEXT = [ FileExt.TXT ]
    IMAGE = [ FileExt.PNG ]
    AUDIO = [ FileExt.MP3, FileExt.WAV, FileExt.OGG ]

class Helpers():
    def data_path() -> str:
        #if exe, locate temp directory
        try:
            #PyQt uses '/' separator, regardless of operating system
            return sys._MEIPASS.replace('\\', '/') + '/'

        #if pyw, use local 'data' directory
        except AttributeError:
            return './'

    def natural_keys(text: str):
        return [ Helpers.atoi(c) for c in re.split(r'(\d+)', text) ]

    def atoi(text: str):
        return int(text) if text.isdigit() else text

    def to_internal_name(title: str) -> str:
        ascii_title = unidecode.unidecode(title)                                            #transliterate unicode letters to ascii
        numname_title = ''.join([ DigitNameDict.get(i, i) for i in ascii_title.lower() ])   #convert upper to lower-case, convert numbers to words
        internal_name = ''.join([ i for i in numname_title if i.isalpha() ])                #strip non-alphabetic characters
        return internal_name

class Assets():
    APP_ICON =              Helpers.data_path() + 'data/jukebox_256.ico'
    FONT_MC_LARGE =         Helpers.data_path() + 'data/minecraft-ten.ttf'
    ICON_ICON_EMPTY =       Helpers.data_path() + 'data/image-empty.png'
    ICON_TRACK_EMPTY =      Helpers.data_path() + 'data/track-empty.png'
    ICON_PACK_EMPTY =       Helpers.data_path() + 'data/pack-empty.png'
    ICON_NEW_DISC =         Helpers.data_path() + 'data/track-new.png'
    ICON_MP3 =              Helpers.data_path() + 'data/track-mp3.png'
    ICON_WAV =              Helpers.data_path() + 'data/track-wav.png'
    ICON_OGG =              Helpers.data_path() + 'data/track-ogg.png'
    ICON_ARROW_UP =         Helpers.data_path() + 'data/arrow-up.png'
    ICON_ARROW_DOWN =       Helpers.data_path() + 'data/arrow-down.png'
    ICON_ARROW_UP_DIS =     Helpers.data_path() + 'data/arrow-up-disabled.png'
    ICON_ARROW_DOWN_DIS =   Helpers.data_path() + 'data/arrow-down-disabled.png'
    ICON_DELETE =           Helpers.data_path() + 'data/delete-btn.png'

class StyleProperties():
    BASE = 'base'
    DRAG_HELD = 'drag_held'
    ALPHA =     'alpha'
    DISABLED =  'disabled'
    PRESSED =   'pressed'
    HOVER =     'hover'
    ERROR =     'error'

#class to contain most of the UI-displayed strings
class DisplayStrings():
    STR_PACKPNG_TITLE =     "Pack icon (optional)"
    STR_PACKNAME_TITLE =    "Pack name"
    STR_VERSION_TITLE =     "Game version"
    STR_OFFSET_TITLE =      "CustomModelData offset"
    STR_ZIP_TITLE =         "Generate pack as .zip"
    STR_MIXMONO_TITLE =     "Mix stereo tracks to mono"
    STR_DP_VER_TITLE =      "Use legacy datapack"
    STR_KEEPTMP_TITLE =     "Keep intermediate converted files"

    STR_PACKPNG_TOOLTIP =   "Optional in-game icon. Auto-fills if you put a 'pack.png' in the same folder as the app."
    STR_PACKNAME_TOOLTIP =  "The name Minecraft will use to reference your pack."
    STR_VERSION_TOOLTIP =   "The version of Minecraft in which your pack will work best."
    STR_OFFSET_TOOLTIP =    "Helps prevent discs in multiple packs from colliding with each other."
    STR_ZIP_TOOLTIP =       "Packs are generated as .zip files instead of folders."
    STR_MIXMONO_TOOLTIP =   "Tracks play near the jukebox, not 'inside your head'."
    STR_DP_VER_TOOLTIP =    "1.19.3 and earlier only supports the legacy datapack."
    STR_KEEPTMP_TOOLTIP =   "Save a copy of converted files so pack generation can go faster next time."

#dictionary to associate Status : status message string
StatusMessageDict = {
    Status.SUCCESS:                 "Successfully generated datapack and resourcepack!",
    Status.LIST_EMPTY:              "Provide at least one track to generate a pack.",
    Status.LIST_UNEVEN_LENGTH:      "Some tracks are missing an icon or a music file.",
    Status.IMAGE_FILE_MISSING:      "Couldn't find icon file. It may have been moved or deleted.",
    Status.BAD_IMAGE_TYPE:          "Icon file is not in a supported format.",
    Status.TRACK_FILE_MISSING:      "Couldn't find music file. It may have been moved or deleted.",
    Status.BAD_TRACK_TYPE:          "Music file is not in a supported format.",
    Status.BAD_INTERNAL_NAME:       "Invalid track name. Make sure all tracks show a subtitle.",
    Status.PACK_IMAGE_MISSING:      "Couldn't find pack icon file.",
    Status.BAD_PACK_IMAGE_TYPE:     "Pack icon is not in a supported format.",
    Status.BAD_OGG_CONVERT:         "Failed to convert some tracks to '.ogg' format.",
    Status.BAD_ZIP:                 "Failed to generate as '.zip'. Packs have been left as folders.",
    Status.IMAGE_FILE_NOT_GIVEN:    "Some tracks are missing an icon.",
    Status.TRACK_FILE_NOT_GIVEN:    "Some tracks are missing a music file.",
    Status.BAD_MP3_META:            "Failed to remove mp3 metadata while converting.",
    Status.BAD_UNICODE_CHAR:        "Couldn't use track name. Try removing uncommon characters.",
    Status.FFMPEG_CONVERT_FAIL:     "FFmpeg failed while converting a track to '.ogg' format.",
    Status.DUP_INTERNAL_NAME:       "Some tracks have the same name. Try removing duplicate tracks.",
    Status.BAD_OGG_META:            "Failed to detect ogg file length while converting."
}

#dictionary to associate Status : sticky state
StatusStickyDict = {
    Status.SUCCESS:                 False,
    Status.LIST_EMPTY:              False,
    Status.LIST_UNEVEN_LENGTH:      False,
    Status.IMAGE_FILE_MISSING:      False,
    Status.BAD_IMAGE_TYPE:          False,
    Status.TRACK_FILE_MISSING:      False,
    Status.BAD_TRACK_TYPE:          False,
    Status.BAD_INTERNAL_NAME:       False,
    Status.PACK_IMAGE_MISSING:      False,
    Status.BAD_PACK_IMAGE_TYPE:     False,
    Status.BAD_OGG_CONVERT:         True,
    Status.BAD_ZIP:                 True,
    Status.IMAGE_FILE_NOT_GIVEN:    False,
    Status.TRACK_FILE_NOT_GIVEN:    False,
    Status.BAD_MP3_META:            True,
    Status.BAD_UNICODE_CHAR:        True,
    Status.FFMPEG_CONVERT_FAIL:     True,
    Status.DUP_INTERNAL_NAME:       True,
    Status.BAD_OGG_META:            True
}

#dictionary to associate digit : digit name
DigitNameDict = {
    '1':    'one',
    '2':    'two',
    '3':    'three',
    '4':    'four',
    '5':    'five',
    '6':    'six',
    '7':    'seven',
    '8':    'eight',
    '9':    'nine',
    '0':    'zero'
}

#dictionary to associate game version : pack format version
PackFormatsDict = {
    '1.20':             {'dp':13, 'rp':14},
    '1.19.4':           {'dp':12, 'rp':13},
    '1.19.3':           {'dp':10, 'rp':12},
    '1.19 - 1.19.2':    {'dp':10, 'rp':9},
    '1.18.2':           {'dp':9,  'rp':8},
    '1.18 - 1.18.1':    {'dp':8,  'rp':8},
    '1.17':             {'dp':7,  'rp':7},
    '1.16.2 - 1.16.5':  {'dp':6,  'rp':6},
    '1.16 - 1.16.1':    {'dp':5,  'rp':5},
    '1.15':             {'dp':5,  'rp':5},
    '1.14':             {'dp':4,  'rp':4}
}

#dictionary to track desired datapack version
#   v2.x only supported in 1.19.4 and higher
#   v1.x offered in 1.19.4 and higher for compatibility
#   not currently used for anything
DatapackVersionDict = {
    'v2.x': 2,
    'v1.x': 1
}



#dataclasses to collect DiscList contents for pack generation
@dataclass
class DiscListEntryContents:
    texture_file:   str = ""
    track_file:     str = ""
    title:          str = ""
    internal_name:  str = ""
    length:         int = 0

#TODO: use iter and next so you don't have to iterate over entries?
@dataclass
class DiscListContents:
    entries: List[DiscListEntryContents] = field(default_factory=list)

    def __len__(self):
        return len(self.entries)

    @property
    def texture_files(self):
        return [entry.texture_file for entry in self.entries]

    @property
    def track_files(self):
        return [entry.track_file for entry in self.entries]

    @property
    def titles(self):
        return [entry.title for entry in self.entries]

    @property
    def internal_names(self):
        return [entry.internal_name for entry in self.entries]

@dataclass
class GeneratorContents:
    status: Status = Status.LIST_EMPTY
    progress: int = 0
    settings: dict = field(default_factory=dict)
    entry_list: DiscListContents = field(default_factory=DiscListContents)



#dataclass to collect info about SettingsList entries
@dataclass
class SettingContents:
    key: str
    type: SettingType
    label: str
    tooltip: str
    params: Any = None

#list to store settings tab contents
SettingsListContents = [
    SettingContents(key='pack',         type=SettingType.PACKPNG,   label=DisplayStrings.STR_PACKPNG_TITLE,     tooltip=DisplayStrings.STR_PACKPNG_TOOLTIP      ),
    SettingContents(key='version',      type=SettingType.DROPDOWN,  label=DisplayStrings.STR_VERSION_TITLE,     tooltip=DisplayStrings.STR_VERSION_TOOLTIP,     params=PackFormatsDict),
#   SettingContents(key='offset',       type=SettingType.NUM_ENTRY, label=DisplayStrings.STR_OFFSET_TITLE,      tooltip=DisplayStrings.STR_OFFSET_TOOLTIP,      params=Constants.CUSTOM_MODEL_DATA_MAX),
    SettingContents(key='name',         type=SettingType.TXT_ENTRY, label=DisplayStrings.STR_PACKNAME_TITLE,    tooltip=DisplayStrings.STR_PACKNAME_TOOLTIP,    params=Constants.DEFAULT_PACK_NAME),
    SettingContents(key='zip',          type=SettingType.CHECK,     label=DisplayStrings.STR_ZIP_TITLE,         tooltip=DisplayStrings.STR_ZIP_TOOLTIP          ),
    SettingContents(key='mix_mono',     type=SettingType.CHECK,     label=DisplayStrings.STR_MIXMONO_TITLE,     tooltip=DisplayStrings.STR_MIXMONO_TOOLTIP      ),
    SettingContents(key='legacy_dp',    type=SettingType.CHECK,     label=DisplayStrings.STR_DP_VER_TITLE,      tooltip=DisplayStrings.STR_DP_VER_TOOLTIP       ),
#   SettingContents(key='keep_tmp',     type=SettingType.CHECK,     label=DisplayStrings.STR_KEEPTMP_TITLE,     tooltip=DisplayStrings.STR_KEEPTMP_TOOLTIP      )
]



#Style definitions
GenerateButtonColorsDict = {
    'background-color': {
        'base':     QColor(32,32,32),
        'hover':    QColor(32,32,32),
        'pressed':  QColor(32,32,32),
        'disabled': QColor(32,32,32)
    },

    'border-outer-color': {
        'base':     QColor(0,0,0),
        'hover':    QColor(0,0,0),
        'pressed':  QColor(255,255,255),
        'disabled': QColor(0,0,0)
    },

    'border-left-color': {
        'base':     QColor(49,108,66),
        'hover':    QColor(49,108,66),
        'pressed':  QColor(49,108,66),
        'disabled': QColor(49,108,66)
    },

    'border-top-color': {
        'base':     QColor(98,202,85),
        'hover':    QColor(98,202,85),
        'pressed':  QColor(32,75,45),
        'disabled': QColor(65,136,57)
    },

    'border-right-color': {
        'base':     QColor(49,108,66),
        'hover':    QColor(49,108,66),
        'pressed':  QColor(49,108,66),
        'disabled': QColor(49,108,66)
    },

    'border-bottom-color': {
        'base':     QColor(32,75,45),
        'hover':    QColor(32,75,45),
        'pressed':  QColor(74,162,53),
        'disabled': QColor(22,52,31)
    },

    'button-color': {
        'base':     QColor(62,139,78),
        'hover':    QColor(68,150,88),
        'pressed':  QColor(62,140,78),
        'disabled': QColor(41,93,52)
    }
}

CSS_STYLESHEET = """
CentralWidget {
    padding: 0;
    border: 0;
}

QFrame#GenFrame {
    background-color: rgb(32, 32, 32);
}

QProgressBar#GenProgress {
    border-top: 2px solid qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(0,0,0,0.5), stop:1 rgba(0,0,0,0));
    border-left: 2px solid qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0,0,0,0.5), stop:1 rgba(0,0,0,0));
    background-color: rgb(72, 102, 78);
}

QProgressBar#GenProgress::chunk {
    border: 0;
    padding: 0;
    background-color: rgb(46, 170, 78);
}

QLabel#GenLabel {
    color: white;
    font-size: 32px;
}

QLabel#GenLabel[hover="true"] {
    font-size: 34px;
}

QLabel#GenLabel[pressed="true"] {
    font-size: 31px;
}

QLabel#GenLabel[disabled="true"] {
    color: lightgray;
    font-size: 32px;
}



StatusDisplayWidget {
    border: 0;
    padding: 10px 10px 10px 5px;
    background-color: rgba(62, 139, 78, 0.75);
    color: white;
    font-size: 16px;
}

StatusDisplayWidget:hover[error="false"] {
    background-color: rgba(68, 150, 88, 0.75);
}

StatusDisplayWidget[error="true"] {
    background-color: rgba(168, 33, 36, 0.7);
}

StatusDisplayWidget:hover[error="true"] {
    background-color: rgba(178, 43, 46, 0.7);
}



QTabWidget::pane {
    padding: 0;
    border: 0;
    background-color: rgb(32, 32, 32);
}

QTabWidget::tab-bar {
}

QTabBar {
    padding: 0;
    border: 0;
    background-color: rgb(32, 32, 32);
}

QTabBar::tab {
    height: 40px;
    font-weight: normal;
    font-size: 16px;
    color: lightgray;
    background-color: rgb(32, 32, 32);
}

QTabBar::tab:selected {
    font-weight: bold;
    color: white;
}

QTabBar::tab:hover {
    color: white;
}



QScrollArea {
    padding: 0;
    border: 0;
}

QScrollBar:vertical {
    padding: 0;
    border: 0;
    background-color: rgb(32, 32, 32);
}

QScrollBar::handle:vertical {
    background-color: rgb(72, 72, 72);
    min-height: 0px;
}

QScrollBar::handle:vertical:hover {
    background-color: rgb(96, 96, 96);
}

QScrollBar::add-line:vertical {
    border: none;
    background: none;
    width: 0px;
    height: 0px;
}

QScrollBar::sub-line:vertical {
    border: none;
    background: none;
    width: 0px;
    height: 0px;
}



SettingsList {
    background-color: rgb(48, 48, 48)
}

SettingsListEntry#PACKPNG {
    border: 0;
    /* border-bottom: 4px solid qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgb(32,32,32), stop:0.8 rgba(0,0,0,0), stop:1 rgb(32,32,32)); */
    border-bottom: 2px solid rgb(72, 72, 72);
}

QWidget#SettingsChildWidget {
    background-color: rgb(48, 48, 48);
}

QLabel#SettingLabel {
    color: lightgray;
    font-weight: normal;
    font-size: 16px;
}

QComboBox {
    border: 1px solid rgb(100, 100, 100);
    color: white;
    font-size: 16px;
    background-color: rgb(48, 48, 48);
    selection-background-color: rgb(57, 130, 73);
    width: 50px;
    height: 30px;
}

QComboBox QAbstractItemView {
    border: 0;
    font-size: 16px;
    background-color: rgb(6, 6, 6);
}

QComboBox:hover {
    background-color: rgb(72, 72, 72);
}

QComboBox::drop-down {
    border: 0;
    width: 30px;
    height: 30px;
}

QComboBox::down-arrow {
    background: url(./data/arrow-down.png) no-repeat center;
}

QCheckBox::indicator {
    border: 0;
    width: 20px;
    height: 20px;
}

QCheckBox::indicator:unchecked {
    background: url(./data/check-bg-unchecked.png) no-repeat center;
}

QCheckBox::indicator:unchecked:hover {
    background: url(./data/check-bg-unchecked-hover.png) no-repeat center;
}

QCheckBox::indicator:checked {
    background: url(./data/check-bg-checked.png) no-repeat center;
}

QCheckBox::indicator:checked:hover {
    background: url(./data/check-bg-checked-hover.png) no-repeat center;
}



DiscList {
    background-color: rgb(48, 48, 48);
}

QWidget#DiscListChildWidget {
    background-color: rgb(48, 48, 48);
}

NewDiscButton {
    border-top: 4px solid qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 black, stop:1 rgba(0,0,0,0));
    border-bottom: 3px solid qlineargradient(x1:0, y1:1, x2:0, y2:0, stop:0 rgb(24,24,24), stop:1 rgba(0,0,0,0));
    border-left: 4px solid qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 black, stop:1 rgba(0,0,0,0));
    border-right: 3px solid qlineargradient(x1:1, y1:0, x2:0, y2:0, stop:0 rgb(24,24,24), stop:1 rgba(0,0,0,0));

    font-size: 48px;
    color: gray;
    background-color: rgb(32, 32, 32);
}

NewDiscButton:hover {
    color:lightgray;
    background-color: rgb(72, 72, 72);
}

NewDiscButton:hover[drag_held="true"] {
}

NewDiscEntry {
    padding: 5px;
    background-color: rgb(48, 48, 48);
}



DiscListEntry {
    padding: 1px;
    border-bottom: 2px solid rgb(72, 72, 72);
    background-color: rgb(48, 48, 48);
}

MultiDragDropButton {
    background-color: rgb(48, 48, 48);
    border: 5px solid rgb(48, 48, 48);
}

MultiDragDropButton[drag_held="true"] {
    border: 5px solid rgb(51, 178, 45);
}

MultiDragDropButton[alpha="9"] {
    border: 5px solid rgba(51, 178, 45, 0.9);
}

MultiDragDropButton[alpha="8"] {
    border: 5px solid rgba(51, 178, 45, 0.8);
}

MultiDragDropButton[alpha="7"] {
    border: 5px solid rgba(51, 178, 45, 0.7);
}

MultiDragDropButton[alpha="6"] {
    border: 5px solid rgba(51, 178, 45, 0.6);
}

MultiDragDropButton[alpha="5"] {
    border: 5px solid rgba(51, 178, 45, 0.5);
}

MultiDragDropButton[alpha="4"] {
    border: 5px solid rgba(51, 178, 45, 0.4);
}

MultiDragDropButton[alpha="3"] {
    border: 5px solid rgba(51, 178, 45, 0.3);
}

MultiDragDropButton[alpha="2"] {
    border: 5px solid rgba(51, 178, 45, 0.2);
}

MultiDragDropButton[alpha="1"] {
    border: 5px solid rgba(51, 178, 45, 0.1);
}

QFrame#MultiDragDropButtonFrame {
    border-top: 4px solid qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 black, stop:1 rgba(0,0,0,0));
    border-bottom: 3px solid qlineargradient(x1:0, y1:1, x2:0, y2:0, stop:0 rgb(32,32,32), stop:1 rgba(0,0,0,0));
    border-left: 4px solid qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 black, stop:1 rgba(0,0,0,0));
    border-right: 3px solid qlineargradient(x1:1, y1:0, x2:0, y2:0, stop:0 rgb(32,32,32), stop:1 rgba(0,0,0,0));

    background-color: rgb(32, 32, 32);
}

QFrame#MultiDragDropButtonFrame:hover[drag_held="true"] {
    background-color: rgb(72, 72, 72);
}

QFrame#MultiDragDropButtonFrame:hover {
    background-color: rgb(72, 72, 72);
}

QLineEdit {
    padding-left: 10px;
    padding-right: 10px;
    padding-top: 4px;
    padding-bottom: 4px;

    color: lightgray;
    font-size: 16px;
    border-radius: 2px;

    background-color: rgb(32, 32, 32);
}

QMultiDragDropLineEdit[drag_held="true"] {
    border: 1px solid rgb(51, 178, 45);
}

QMultiDragDropLineEdit[alpha="9"] {
    border: 1px solid rgba(51, 178, 45, 0.9);
}

QMultiDragDropLineEdit[alpha="8"] {
    border: 1px solid rgba(51, 178, 45, 0.8);
}

QMultiDragDropLineEdit[alpha="7"] {
    border: 1px solid rgba(51, 178, 45, 0.7);
}

QMultiDragDropLineEdit[alpha="6"] {
    border: 1px solid rgba(51, 178, 45, 0.6);
}

QMultiDragDropLineEdit[alpha="5"] {
    border: 1px solid rgba(51, 178, 45, 0.5);
}

QMultiDragDropLineEdit[alpha="4"] {
    border: 1px solid rgba(51, 178, 45, 0.4);
}

QMultiDragDropLineEdit[alpha="3"] {
    border: 1px solid rgba(51, 178, 45, 0.3);
}

QMultiDragDropLineEdit[alpha="2"] {
    border: 1px solid rgba(51, 178, 45, 0.2);
}

QMultiDragDropLineEdit[alpha="1"] {
    border: 1px solid rgba(51, 178, 45, 0.1);
}

QFocusLineEdit {
    border: 1px solid rgb(48, 48, 48);
}

QFocusLineEdit:focus {
    color: white;
    background-color: rgb(6, 6, 6);
    border: 1px solid lightgray;
}

QSettingLineEdit {
    padding-left: 2px;
    padding-right: 0px;
    padding-top: 0px;
    padding-bottom: 0px;

    width: 80px;
    height: 30px;

    color: white;
    border-radius: 0px;
    border: 1px solid rgb(100, 100, 100);
    background-color: rgb(48, 48, 48);
}

QSettingLineEdit:hover {
    background-color: rgb(72, 72, 72);
}

QSettingLineEdit:hover:focus {
    background-color: rgb(6, 6, 6);
}

QAlphaLineEdit {
    width: 160px;
}

QLabel#INameLabel {
    color: gray;
    font-style: italic;
    background-color: rgb(48, 48, 48);
}

DeleteButton {
    border: 0;
    background-color: rgb(48, 48, 48);
    background: url(./data/delete-btn.png) no-repeat center;
}

DeleteButton:hover {
    background: url(./data/delete-btn-hover.png) no-repeat center;
}

ArrowButton {
    border: 0;
    background-color: rgb(48, 48, 48);
}

ArrowButton:hover {
    background-color: rgb(96, 96, 96);
}

QToolTip {
    border: 0;
    color: white;
    font-size: 17px;
    background-color: rgb(6, 6, 6);
}
""".replace('./', Helpers.data_path() )


