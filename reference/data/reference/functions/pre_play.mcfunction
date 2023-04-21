execute store result score @s imd_disc_id run data get block ~ ~ ~ RecordItem.tag.CustomModelData
function {datapack_name}:play_duration
scoreboard players set @s imd_stop_11_time 2
function {datapack_name}:watchdog_reset_tickcount
execute as @a[distance=..64] run function {datapack_name}:register_jukebox_listener
