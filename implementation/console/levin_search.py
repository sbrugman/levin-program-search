"""This file add the console interface to the package."""
import argparse
import collections
import json
from pathlib import Path
from sys import argv
from typing import Union
import sys

import attr

sys.path.insert(0, r"../")
from initial_primitives import InitialPrimitives
from weight_primitives import WeightPrimitives
from console.utils import absolute_path_extension
from levin_search import main_levin_search
from task import Tasks
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
        "--work_tape_size", default=1, help="The size of the work tape", type=int
    )

    parser.add_argument(
        "--program_tape_size",
        default=1000,
        help="The size of the program tape",
        type=int,
    )

    parser.add_argument(
        "--primitives_set",
        default="DEFAULT",
        choices=["DEFAULT", "WEIGHT"],
        help="Use the following set of primitives",
    )

    parser.add_argument(
        "task",
        choices=list(Tasks),
        type=Tasks.from_string,
        help="Which task to run? Tasks can be defined in `task.py`",
    )

    parser.add_argument(
        "search_length", type=int, help="Search for programs up to this length."
    )

    parser.add_argument(
        "--search_log",
        type=absolute_path_extension([".csv"]),
        help="Store the log of the deterministic levin search process (.csv).",
    )

    parser.add_argument(
        "--solutions_file",
        type=absolute_path_extension([".json"]),
        help="Store the solutions found in this file (.json)",
    )

    # or solutions dir
    parser.add_argument(
        "solutions_dir",
        type=Path,
        help="Directory to store solutions, created if not exists",
    )

    return parser.parse_args(args)


def main(args=None) -> None:
    """ Run the levin search.

    Args:
      args: Arguments for the programme (Default value=None).
    """

    # Parse the arguments
    args = parse_args(args)

    if args.primitives_set == "WEIGHT":
        primitives = WeightPrimitives()
    else:
        primitives = InitialPrimitives()

    search_state = main_levin_search(
        args.task,
        primitives,
        args.work_tape_size,
        args.program_tape_size,
        args.search_length,
        search_log_file=args.search_log,
    )
    # Search state
    if args.search_log:
        with args.search_log.with_suffix(".json").open("w") as f:
            json.dump(
                attr.asdict(
                    search_state,
                    filter=lambda attrib, _: attrib.name
                    not in ["logger", "memory", "solutions"],
                ),
                f,
            )

    solutions = [attr.asdict(s) for s in search_state.solutions]

    # Solutions file
    if args.solutions_file:
        with args.solutions_file.open("w") as f:
            json.dump(solutions, f)

    # Solutions dir
    args.solutions_dir.mkdir(exist_ok=True, parents=True)
    counter = collections.Counter()
    for solution in solutions:
        file_name = (
            args.solutions_dir
            / f"phase{solution['phase']}_solution{counter[solution['phase']]}.json"
        )

        solution["program"] = [int(c) for c in solution["program"]]
        file_name.write_text(json.dumps(solution))

        counter[solution["phase"]] += 1


if __name__ == "__main__":
    main(args=argv[1:])
