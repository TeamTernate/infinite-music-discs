#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack command builder module
#Generation tool, datapack design, and resourcepack design by link2_thepast
#Command builder module core design by LucMellee

from dataclasses import dataclass
from enum import Enum



class ItemSlot(Enum):
    WEAPON_MAINHAND = "weapon.mainhand"
    WEAPON_OFFHAND = "weapon.offhand"
    ARMOR_CHEST = "armor.chest"
    ARMOR_FEET = "armor.feet"
    ARMOR_HEAD = "armor.head"
    ARMOR_LEGS = "armor.legs"
    CONTAINER = "container"
    ENDERCHEST = "enderchest"
    HOTBAR = "hotbar"
    INVENTORY = "inventory"
    HORSE_SADDLE = "horse.saddle"
    HORSE_CHEST = "horse.chest"
    HORSE_ARMOR = "horse.armor"

    def get_value_by_pack_format(self, pack_format, slot_id: int = None):
        if slot_id is None:
            return self.value
        else:
            return self.value + '.' + str(slot_id)



# Supports minecraft 1.13+
@dataclass
class ReplaceItemCommand:
    # x, y and z coordinates, space separated
    block_pos: str = None
    # Target entity is either block or @a, @e etc.
    target_entity: str = None
    slot: ItemSlot = None
    slotId: int = None
    item: str = None
    count: int = None

    change_version = 7

    # If in the future new changes are made to the command, add the new structure here.
    def command_by_pack_format(self, pack_format):
        if pack_format >= self.change_version:
            if self.target_entity != "block":
                return "item replace entity " \
                       + self.target_entity \
                       + " " \
                       + self.slot.get_value_by_pack_format(pack_format) \
                       + " with " \
                       + self.item \
                       + (" " + str(self.count) if self.count is not None else "")
            else:
                return "item replace block " \
                       + self.block_pos \
                       + self.slot.get_value_by_pack_format(pack_format) \
                       + " with " \
                       + self.item \
                       + (" " + str(self.count) if self.count is not None else "")

        else:
            if self.target_entity != "block":
                return "replaceitem entity " \
                       + self.target_entity \
                       + " "  \
                       + self.slot.get_value_by_pack_format(pack_format, self.slotId) \
                       + " " \
                       + self.item \
                       + (" " + str(self.count) if self.count is not None else "")
            else:
                return "replaceitem block " \
                       + self.block_pos \
                       + " " \
                       + self.slot.get_value_by_pack_format(pack_format, self.slotId) \
                       + " " \
                       + self.item \
                       + (" " + str(self.count) if self.count is not None else "")
