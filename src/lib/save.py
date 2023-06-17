# -*- coding: utf-8 -*-
# Save current track config

import json
import dataclasses
from src.definitions import DiscListContents

class Config:
    def save(self, tracks: DiscListContents, location: str):
        with open(location, "w", encoding="utf8") as file:
            jsonable_tracks = [dataclasses.asdict(track) for track in tracks.entries]
            json.dump(jsonable_tracks, file)

    def load(self, location: str) -> DiscListContents:
        with open(location, "r", encoding="utf8") as file:
            try:
                save_content: list[dict(DiscListContents)] = json.load(file)
                return DiscListContents([dataclasses.asdict(track) for track in save_content])
            except Exception as error:
                # file seems corrupted
                raise error
