from src.cli.cli_parser import CLIParser
from src.cli.packer import HeadlessGeneratePackWorker
from os import chdir

if __name__ == '__main__':
    cli_parser = CLIParser()
    musics = cli_parser.get_music()
    setting = cli_parser.get_settings()
    chdir(cli_parser.output_dir)
    worker = HeadlessGeneratePackWorker(musics, setting)
    worker.run()
