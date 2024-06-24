# -*- coding: utf-8 -*-
# Save current track config

import dataclasses
import json

from src.definitions import DiscListContents, DiscListEntryContents

from .exceptions import LoadExceptions

# I think we should always have a version key
# at the top of the save file
# {
#     "version": 1,
#     ...
# }


# Base class for save generators
class BaseGenerator:

    @staticmethod
    def generate(content: DiscListContents) -> dict:
        ...

    @staticmethod
    def load(content: dict) -> DiscListContents:
        ...


# Version 1 save generator
class V1Generator(BaseGenerator):
    version = 1

    @staticmethod
    def generate(content: DiscListContents) -> dict:
        return {
            "version": 1,
            "tracks": [track.__dict__ for track in content.entries],
        }

    @staticmethod
    def load(content: dict) -> DiscListContents:
        return DiscListContents([
            DiscListEntryContents(**track) for track in content["tracks"]
        ])


generators: dict[int, BaseGenerator] = {
    1: V1Generator,
}


class TracksSave:
    location: str
    generator: BaseGenerator

    def __init__(self, location: str = "save.json", version: int = 1): # default to newest version
        self.location = location
        self.generator = generators[version]
        pass

    def save(self, tracks: DiscListContents):
        with open(self.location, "w", encoding = "utf8") as file:
            content = self.generator.generate(tracks)
            try:
                json.dump(content, file)
            except OSError as error:
                raise SaveExceptions.OSError() from error

class TracksLoad:
    location: str
    generator: BaseGenerator | None
    
    def __init__(self, location: str = "save.json", version: int | None = None):
        self.location = location
        self.generator = generators[version] if version is not None else None
        pass
    
    def load(self, version: int | None = None) -> DiscListContents:
        with open(self.location, "r", encoding = "utf8") as file:
            try:
                content = json.load(file)
                
                if version is not None:
                    version = content.get("version")
                
                # guessing generator based on version in save file
                if self.generator is None:
                    try:
                        self.generator = generators[version]
                    except KeyError as error:
                        raise LoadExceptions.InvalidVersion() from error

                return self.generator.load(content)
            except Exception as error:
                # file seems corrupted
                raise LoadExceptions.JSONDecodeError() from error
