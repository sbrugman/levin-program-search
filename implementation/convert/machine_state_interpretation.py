import json
from pathlib import Path
from typing import Sequence


def generate_table(log_file: Path, output_file: Path, op_names: Sequence[str]) -> None:
    """Generate a table of instructions when provided with a valid program

    Args:
        log_file: the file containing the program
        output_file: the file to write the table to

    Examples:
        | Address | Contents | Interpretation |
        |---------|----------|----------------|
        | 0		  | 1		 | OUTPUT		  |
        | 1		  | 0		 | address 		  |
        | 2		  | 2		 | JUMP			  |
        | 3		  | 0		 | address		  |

    Notes:
        Invalid programs will lead to unexpected results
    """
    ips = set()
    program = None

    with log_file.open() as f:
        for line in f:
            data = json.loads(line)
            ips.add(data["state"]["instruction_pointer"])
            program = data["storage"]["program_tape"]

    table = f"| Address | Contents | Interpretation |\n"
    table += f"|---------|----------|----------------|\n"
    for address, contents in enumerate(program):
        if address in ips:
            inter = op_names[contents]
        else:
            inter = "address"

        table += f"| {address: <7} | {contents: <8} | {inter: <14} |\n"

    output_file.write_text(table)
