execute as @s[tag=!imd_is_playing] if block ~ ~ ~ minecraft:jukebox{{IsPlaying:1b}} run function {datapack_name}:jukebox_on_play
execute as @s[tag=imd_is_playing] unless block ~ ~ ~ minecraft:jukebox{{IsPlaying:1b}} run function {datapack_name}:jukebox_on_stop
