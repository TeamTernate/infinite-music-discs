pyinstaller main.pyw --onefile --clean --noconfirm ^
--add-data "data/*;data" ^
--name "infinite-music-discs" ^
--icon "data/jukebox_256.ico" ^
--distpath bin
