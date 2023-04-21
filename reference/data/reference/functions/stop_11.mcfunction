execute store result score @s imd_player_id run data get entity @s data.Listeners_11[0]
data remove entity @s data.Listeners_11[0]
execute as @a if score @s imd_player_id = @e[type=marker,tag=imd_jukebox_marker,distance=..0.1,limit=1] imd_player_id run stopsound @s record minecraft:music_disc.11
execute if data entity @s data.Listeners_11[0] run function {datapack_name}:stop_11
execute unless data entity @s data.Listeners_11[0] run tag @s add imd_stopped_11
