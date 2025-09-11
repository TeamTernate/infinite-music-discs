from typing import TypedDict


class DPRPVerPair(TypedDict):
    dp: int
    rp: int


class Settings(TypedDict):
    legacy_dp: bool
    mix_mono: bool
    name: str
    pack: str
    skip_proc: bool
    version: DPRPVerPair
    zip: bool
