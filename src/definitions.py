#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#Infinite Music Discs constants definition module
#Generation tool, datapack design, and resourcepack design by link2_thepast

import re
import sys
from enum import Enum
from src.generator import Status

#constants
class Constants():
    MAX_DRAW_MULTI_DRAGDROP = 10
    STATUS_MESSAGE_SHOW_TIME_MS = 10000
    CUSTOM_MODEL_DATA_MAX = 16777000
    DEFAULT_PACK_NAME = 'custom_music_discs'



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

class FileExt():
    PNG = 'png'
    MP3 = 'mp3'
    WAV = 'wav'
    OGG = 'ogg'
    TXT = 'txt'

class Helpers():
    def data_path():
        #if exe, locate temp directory
        try:
            #PyQt uses '/' separator, regardless of operating system
            return sys._MEIPASS.replace('\\', '/') + '/'

        #if pyw, use local 'data' directory
        except Exception:
            return './'

    def natural_keys(text):
        return [ Helpers.atoi(c) for c in re.split(r'(\d+)', text) ]

    def atoi(text):
        return int(text) if text.isdigit() else text

class Assets():
    APP_ICON =              Helpers.data_path() + 'data/jukebox_256.ico'
    FONT_MC_LARGE =         Helpers.data_path() + 'data/minecraft-ten.ttf'
    ICON_ICON_EMPTY =       Helpers.data_path() + 'data/image-empty.png'
    ICON_TRACK_EMPTY =      Helpers.data_path() + 'data/track-empty.png'
    ICON_PACK_EMPTY =       Helpers.data_path() + 'data/pack-empty.png'
    ICON_NEW_DISC =         Helpers.data_path() + 'data/new-disc.png'
    ICON_MP3 =              Helpers.data_path() + 'data/track-mp3.png'
    ICON_WAV =              Helpers.data_path() + 'data/track-wav.png'
    ICON_OGG =              Helpers.data_path() + 'data/track-ogg.png'
    ICON_ARROW_UP =         Helpers.data_path() + 'data/arrow-up.png'
    ICON_ARROW_DOWN =       Helpers.data_path() + 'data/arrow-down.png'
    ICON_ARROW_UP_DIS =     Helpers.data_path() + 'data/arrow-up-disabled.png'
    ICON_ARROW_DOWN_DIS =   Helpers.data_path() + 'data/arrow-down-disabled.png'
    ICON_DELETE =           Helpers.data_path() + 'data/delete-btn.png'

class StyleProperties():
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
    STR_KEEPTMP_TITLE =     "Keep intermediate converted files"

    STR_PACKPNG_TOOLTIP =   "Optional in-game icon. Auto-fills if you put a 'pack.png' in the same folder as the app."
    STR_PACKNAME_TOOLTIP =  "The name Minecraft will use to reference your pack."
    STR_VERSION_TOOLTIP =   "The version of Minecraft in which your pack will work best."
    STR_OFFSET_TOOLTIP =    "Helps prevent discs in multiple packs from colliding with each other."
    STR_ZIP_TOOLTIP =       "Packs are generated as .zip files instead of folders."
    STR_MIXMONO_TOOLTIP =   "Tracks play near the jukebox, not 'inside your head'."
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
    Status.BAD_MP3_META:            "Failed to remove mp3 metadata while converting."
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
    '1.18':             8,
    '1.17':             7,
    '1.16.2 - 1.16.5':  6,
    '1.16 - 1.16.1':    5,
    '1.15':             5,
    '1.14':             4
}



#CSS sheets
CSS_STYLESHEET = """
CentralWidget {
    padding: 0;
    border: 0;
}



GenerateButton {
    border: 0;
    background-color: rgb(32,32,32);

    border-outer-color: rgb(0,0,0);
    border-left-color: rgb(49,108,66);
    border-top-color: rgb(98,202,85);
    border-right-color: rgb(49,108,66);
    border-bottom-color: rgb(32,75,45);
    button-color: rgb(62,139,78);
}

GenerateButton[hover="true"] {
    button-color: rgb(68,150,88);
}

GenerateButton[pressed="true"] {
    border-outer-color: rgb(255,255,255);
    border-top-color: rgb(32,75,45);
    border-bottom-color: rgb(74,162,53);
    button-color: rgb(62,140,78);
}

GenerateButton[disabled="true"] {
    border-top-color: rgb(65,136,57);
    border-bottom-color: rgb(22,52,31);
    button-color: rgb(41,93,52);
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

FileButton {
    background-color: rgb(48, 48, 48);
    border: 5px solid rgb(48, 48, 48);
}

FileButton[drag_held="true"] {
    border: 5px solid rgb(51, 178, 45);
}

FileButton[alpha="9"] {
    border: 5px solid rgba(51, 178, 45, 0.9);
}

FileButton[alpha="8"] {
    border: 5px solid rgba(51, 178, 45, 0.8);
}

FileButton[alpha="7"] {
    border: 5px solid rgba(51, 178, 45, 0.7);
}

FileButton[alpha="6"] {
    border: 5px solid rgba(51, 178, 45, 0.6);
}

FileButton[alpha="5"] {
    border: 5px solid rgba(51, 178, 45, 0.5);
}

FileButton[alpha="4"] {
    border: 5px solid rgba(51, 178, 45, 0.4);
}

FileButton[alpha="3"] {
    border: 5px solid rgba(51, 178, 45, 0.3);
}

FileButton[alpha="2"] {
    border: 5px solid rgba(51, 178, 45, 0.2);
}

FileButton[alpha="1"] {
    border: 5px solid rgba(51, 178, 45, 0.1);
}

QFrame#FileButtonFrame {
    border-top: 4px solid qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 black, stop:1 rgba(0,0,0,0));
    border-bottom: 3px solid qlineargradient(x1:0, y1:1, x2:0, y2:0, stop:0 rgb(32,32,32), stop:1 rgba(0,0,0,0));
    border-left: 4px solid qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 black, stop:1 rgba(0,0,0,0));
    border-right: 3px solid qlineargradient(x1:1, y1:0, x2:0, y2:0, stop:0 rgb(32,32,32), stop:1 rgba(0,0,0,0));

    background-color: rgb(32, 32, 32);
}

QFrame#FileButtonFrame:hover[drag_held="true"] {
    background-color: rgb(72, 72, 72);
}

QFrame#FileButtonFrame:hover {
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


