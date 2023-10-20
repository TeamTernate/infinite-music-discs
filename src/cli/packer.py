from src.definitions import DiscListContents
from src.generator import factory as generator_factory


class HeadlessGeneratePackWorker():
    def __init__(self, entry_list: DiscListContents, settings: dict):
        super().__init__()

        self._generator = generator_factory.get(settings)

        self._entry_list = entry_list
        self._settings = settings
        self._progress = 0

    def emit_update_progress(self):
        self._progress += 1


    def generate(self):
        self.run()


    def run(self):

        #total steps = validate + num track conversions + generate dp + generate rp

        self._progress = 0

        #make sure data is valid before continuing
        self._generator.validate(self._entry_list, self._settings)
        self.emit_update_progress()

        #process tracks
        self._generator.create_tmp()
        self._generator.convert_all_to_ogg(self._entry_list, self._settings, self.emit_update_progress)

        #post-process tracks individually
        for e in self._entry_list.entries:
            # e.track_file = self._generator.convert_to_ogg(e, self._settings)
            e.length = self._generator.get_track_length(e)
            e.title = self._generator.sanitize(e)
            self.emit_update_progress()

        #generate datapack
        self._generator.generate_datapack(self._entry_list, self._settings)
        self.emit_update_progress()

        #generate resourcepack
        self._generator.generate_resourcepack(self._entry_list, self._settings)
        self.emit_update_progress()

        #finish up and return to generate()
        self._generator.cleanup_tmp()
        print("Successfully generated datapack and resourcepack!")