execute as @s[scores={{imd_play_time=1..}}] run scoreboard players remove @s imd_play_time 1
execute as @s[scores={{imd_stop_11_time=1..}}] run scoreboard players remove @s imd_stop_11_time 1
execute as @s[scores={{imd_play_time=0}}] run data merge block ~ ~ ~ {{RecordStartTick:-999999L}}
execute as @s[scores={{imd_stop_11_time=0}},tag=!imd_stopped_11] run function {datapack_name}:stop_11
