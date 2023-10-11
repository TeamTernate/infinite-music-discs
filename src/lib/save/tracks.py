# -*- coding: utf-8 -*-
# Save current track config

import dataclasses
import json

from src.definitions import DiscListContents, DiscListEntryContents


# Base class for save generators
class VirtualGenerator:

    @staticmethod
    def generate(content: DiscListContents) -> dict:
        ...

    @staticmethod
    def load(content: dict, force: bool) -> DiscListContents:
        ...


# Version 1 save generator
class V1Generator(VirtualGenerator):
    version = 1

    @staticmethod
    def generate(content: DiscListContents) -> dict:
        return {
            "version": 1,
            "tracks": [track.__dict__ for track in content.entries],
        }

    @staticmethod
    def load(content: dict, force: bool) -> DiscListContents:
        if content["version"] != 1 and not force:
            raise Exception("Invalid save version")

        return DiscListContents([
            DiscListEntryContents(**track) for track in content["tracks"]
        ])


generators: dict[int, VirtualGenerator] = {
    1: V1Generator,
}


class TracksSave:
    location: str
    version: int
    generator: VirtualGenerator

    def __init__(self, location: str = "save.json", version: int = 1):
        self.location = location
        self.version = version
        self.generator = generators[version]
        pass

    def save(self, tracks: DiscListContents):
        with open(self.location, "w", encoding = "utf8") as file:
            content = self.generator.generate(tracks)
            json.dump(content, file)

    def load(self, force: bool = False) -> DiscListContents:
        with open(self.location, "r", encoding = "utf8") as file:
            try:
                content = json.load(file)

                return self.generator.load(content, force)
            except Exception as error:
                # file seems corrupted
                raise error
