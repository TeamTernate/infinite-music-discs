execute if score @e[type=marker,tag=imd_jukebox_marker,distance=..0.1,limit=1] imd_disc_id matches {entry.custom_model_data} run function {datapack_name}:{entry.internal_name}/play
