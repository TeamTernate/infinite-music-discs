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

    # This code supports the 'replaceitem' and 'item replace' command structures.
    # If in the future the command format changes this code can be extended to support that new format.
    def command_by_pack_format(self, pack_format: int):
        new_format = pack_format >= self.change_version
        if self.target_entity == "block":
            return self._generate_command("block", self.block_pos, new_format)
        else:
            return self._generate_command("entity", self.target_entity, new_format)

    def _generate_command(self, base: str, target: str, new_format: bool):
        if new_format:
            return self._generate_new_format_command(base, target)
        return self._generate_old_format_command(base, target)

    # Generates command according to the 'replaceitem' format
    # See https://minecraft.fandom.com/wiki/Commands/replaceitem
    def _generate_old_format_command(self, base: str, target: str):
        return "replaceitem " \
            + base \
            + " " \
            + target \
            + " " \
            + self.slot.get_value_by_pack_format(self.slot_id) \
            + " " \
            + self.item \
            + (" " + str(self.count) if self.count is not None else "")

    # Generates command according to the 'item replace' format
    # See https://minecraft.fandom.com/wiki/Commands/item
    def _generate_new_format_command(self, base: str, target: str):
        return "item replace " \
            + base \
            + " " \
            + target \
            + " " \
            + self.slot.get_value_by_pack_format(self.slot_id) \
            + " with " \
            + self.item \
            + (" " + str(self.count) if self.count is not None else "")
