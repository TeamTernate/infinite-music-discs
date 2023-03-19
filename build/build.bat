pyinstaller main.pyw --onefile --clean --noconfirm ^
--version-file "version.rc" ^
--add-data "data/*;data" ^
--name "imd-gui" ^
--icon "data/jukebox_256.ico" ^
--distpath bin
