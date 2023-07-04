# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack command builder module
#Generation tool, datapack design, and resourcepack design by link2_thepast
#Command builder module core design by theelicht (Luc Mellee)

from dataclasses import dataclass
from enum import Enum


class ItemSlot(Enum):
    # Do not require slot ID
    WEAPON_MAINHAND = "weapon.mainhand"
    WEAPON_OFFHAND = "weapon.offhand"
    ARMOR_CHEST = "armor.chest"
    ARMOR_FEET = "armor.feet"
    ARMOR_HEAD = "armor.head"
    ARMOR_LEGS = "armor.legs"
    HORSE_SADDLE = "horse.saddle"
    HORSE_CHEST = "horse.chest"
    HORSE_ARMOR = "horse.armor"
    # Require slot ID
    CONTAINER = "container"
    ENDERCHEST = "enderchest"
    HOTBAR = "hotbar"
    INVENTORY = "inventory"

    def get_value_by_pack_format(self, slot_id: int = None):
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
    slot_id: int = None
    item: str = None
    count: int = None

    change_version = 7

    # If in the future new changes are made to the command, add the new structure here.
    def command_by_pack_format(self, pack_format: int):
        if pack_format >= self.change_version:
            if self.target_entity != "block":
                return self._generate_command("item replace entity", self.target_entity, True)
            else:
                return self._generate_command("item replace block", self.block_pos, True)

        else:
            if self.target_entity != "block":
                return self._generate_command("replaceitem entity", self.target_entity, False)
            else:
                return self._generate_command("replaceitem block", self.block_pos, False)

    def _generate_command(self, base: str, target: str, new_format: bool):
        return base \
            + " " \
            + target \
            + " " \
            + self.slot.get_value_by_pack_format(self.slot_id) \
            + (" with " if new_format else " ") \
            + self.item \
            + (" " + str(self.count) if self.count is not None else "")
