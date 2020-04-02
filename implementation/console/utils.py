import argparse
from pathlib import Path


def absolute_path(p) -> Path:
    return Path(p).absolute()


def absolute_path_extension(extensions):
    def absolute_path_e(p):
        p = absolute_path(p)
        if p.suffix not in extensions:
            raise argparse.ArgumentTypeError(
                f'allowed extension(s) are {", ".join(extensions)}'
            )
        return p

    return absolute_path_e


def absolute_path_dir():
    def absolute_path_dir_valid(p):
        p = absolute_path(p)
        if not p.is_dir():
            raise argparse.ArgumentTypeError(f"should be a directory")
        return p

    return absolute_path_dir_valid


def parse_program(program: str):
    return [int(cell) for cell in program.split(",")]


def parse_program_file(file_name: str):
    return parse_program(absolute_path_extension([".txt"])(file_name).read_text())


def program_format(program, sep="_"):
    return sep.join(map(str, program))
