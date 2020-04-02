"""This file add the console interface to the package."""
import argparse
from pathlib import Path
from sys import argv
from tempfile import TemporaryDirectory
from typing import Union
import sys

sys.path.insert(0, r"../")

from initial_primitives import InitialPrimitives
from weight_primitives import WeightPrimitives
from console.utils import absolute_path_extension, absolute_path_dir
from convert.machine_state_interpretation import generate_table
from convert.plot_machine_states import plot_machine_states
from version import __version__


def parse_args(args: Union[list, None] = None) -> argparse.Namespace:
    """Parse the command line arguments for levin_search.
    Args:
      args: List of input arguments. (Default value=None).
    Returns:
      Namespace with parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Levin search for Discovering Low Complexity Neural Network Weights"
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
        "program_file",
        type=absolute_path_extension([".jsonl"]),
        help="Which log file to use?",
    )

    subparser = parser.add_subparsers()
    table = subparser.add_parser("table", help="Table with the program instructions")
    table.add_argument(
        "--primitives_set",
        default="DEFAULT",
        choices=["DEFAULT", "WEIGHT"],
        help="Use the following set of primitives",
    )

    table.add_argument(
        "output_file",
        type=absolute_path_extension([".md"]),
        help="Which output file to use (.md)? ",
    )
    table.set_defaults(which="table")

    animation = subparser.add_parser("animation", help="Animate the program run")
    animation.add_argument(
        "--image_dir",
        default=Path(TemporaryDirectory().name),
        type=absolute_path_dir,
        help="A directory to store the animation frames (in .png). If the directory is ",
    )

    animation.add_argument(
        "output_file",
        type=absolute_path_extension([".gif"]),
        help="Which output file to use (.gif)? ",
    )
    animation.set_defaults(which="animation")

    return parser.parse_args(args)


def main(args=None) -> None:
    """ Run the levin search.

    Args:
      args: Arguments for the programme (Default value=None).
    """

    # Parse the arguments
    args = parse_args(args)

    if args.which == "animation":
        plot_machine_states(args.program_file, args.image_dir, args.output_file)
    elif args.which == "table":
        if args.primitives_set == "WEIGHT":
            primitives = WeightPrimitives()
        else:
            primitives = InitialPrimitives()

        generate_table(args.program_file, args.output_file, primitives.get_op_names())
    else:
        raise ValueError("Unknown subroutine")


if __name__ == "__main__":
    main(args=argv[1:])
