"""This file add the console interface to the package."""
import argparse
from sys import argv
from typing import Union
import sys

sys.path.insert(0, r"../")
from initial_primitives import InitialPrimitives
from weight_primitives import WeightPrimitives
from version import __version__
from levin_search import main_run_program
from console.utils import absolute_path_extension, parse_program, parse_program_file


def parse_args(args: Union[list, None] = None) -> argparse.Namespace:
    """Parse the command line arguments for running a program.
    Args:
      args: List of input arguments. (Default value=None).
    Returns:
      Namespace with parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Program Running for Discovering Low Complexity Neural Network Weights"
    )

    # Version
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    # Console specific
    parser.add_argument(
        "--work_tape_size", default=10, help="The size of the work tape", type=int
    )

    parser.add_argument(
        "--program_tape_size",
        default=100,
        help="The size of the program tape",
        type=int,
    )

    parser.add_argument(
        "--n_weights", default=10, help="The number of weights", type=int
    )

    parser.add_argument(
        "--primitives_set",
        default="DEFAULT",
        choices=["DEFAULT", "WEIGHT"],
        help="Use the following set of primitives",
    )

    subparser = parser.add_subparsers()

    file = subparser.add_parser("file")

    file.add_argument(
        "program_file",
        type=parse_program_file,
        help="file with the program stored (.txt)",
    )
    file.set_defaults(which="file")

    program = subparser.add_parser("string")

    program.add_argument(
        "program_string",
        type=parse_program,
        help="a comma separated program (of integers)",
    )
    program.set_defaults(which="string")

    parser.add_argument(
        "log_file",
        type=absolute_path_extension([".jsonl"]),
        help="Store the logs in this file (.jsonl)",
    )

    return parser.parse_args(args)


def main(args=None) -> None:
    """ Run a program.
    Args:
      args: Arguments for the programme (Default value=None).
    """

    # Parse the arguments
    args = parse_args(args)

    if args.which == "string":
        program = args.program_string
    elif args.which == "file":
        program = args.program_file
    else:
        raise ValueError("Unknown subroutine")

    if args.primitives_set == "WEIGHT":
        primitives = WeightPrimitives()
    else:
        primitives = InitialPrimitives()

    main_run_program(
        primitives,
        program,
        args.program_tape_size,
        args.work_tape_size,
        args.n_weights,
        args.log_file,
    )


if __name__ == "__main__":
    main(args=argv[1:])
