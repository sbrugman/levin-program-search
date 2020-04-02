"""This file contains functionality related to the visualisation of the machine state."""
import json
import subprocess
import sys
from pathlib import Path

from jinja2.environment import Template


sys.path.insert(0, r"../")

from paths import implementation_dir
from config import imagemagick_convert_path, pdflatex_path


# https://tex.stackexchange.com/questions/49839/turing-machine-figure
# http://www.texample.net/tikz/examples/turing-machine-2/
def plot_machine_states(
    log_file: Path, image_dir: Path, animation_output_file: Path
) -> None:
    image_dir.mkdir(exist_ok=True)

    with log_file.open("r") as f:
        for line in f:
            program = json.loads(line)
            plot_single_state(program, image_dir)

    make_animation(animation_output_file, image_dir)


def plot_single_state(program, image_dir):
    """Visualise the state of the system.

    Args:
        program: The Program object (program tape, state etc.).
        image_dir: The directory to write the state image to.
    """
    addresses = False

    state = program["state"]
    storage = program["storage"]

    instruction_pointer = state["instruction_pointer"] + -1 * state["min"]

    program_tape = []
    prev_node_name = None
    for i, v in enumerate(storage["work_tape"] + storage["program_tape"]):
        node_name = str(i)
        program_tape.append(
            {
                "node_name": node_name,
                "prev_node_name": prev_node_name,
                "value": v,
                "work_tape": i < (-1 * state["min"]),
            }
        )
        prev_node_name = node_name

    weight_tape = []
    prev_node_name = None
    for i, v in enumerate(list(storage["weights"])):
        node_name = str(i)
        weight_tape.append(
            {"node_name": node_name, "prev_node_name": prev_node_name, "value": int(v)}
        )
        prev_node_name = node_name

    weight_tape.append(
        {"node_name": str(i + 1), "prev_node_name": prev_node_name, "value": " "}
    )
    content = (implementation_dir() / "convert" / "template.tex.jinja").read_text()
    template = Template(content)

    node_name_head = (
        "a" + program_tape[instruction_pointer]["node_name"]
        if addresses
        else "s" + program_tape[instruction_pointer]["node_name"]
    )
    a = template.render(
        program_tape=program_tape,
        weight_tape=weight_tape,
        node_name_first=program_tape[0]["node_name"],
        node_name_last=program_tape[-1]["node_name"],
        addresses=addresses,
        node_name_instruction_head=node_name_head,
        node_name_weight_head="w" + str(state["weight_pointer"]),
        s_align="s" + str(-1 * state["min"]),
        time=state["current_runtime"],
    )
    a = a.replace("\n   \n", "\n")

    if addresses:
        addresses_str = "_addresses"
    else:
        addresses_str = ""

    path = image_dir / f"{state['current_runtime']:08d}{addresses_str}.tex"
    path.write_text(a)

    to_image(path)


def to_image(path):
    # https://www.ghostscript.com/download/gsdnld.html
    subprocess.call(
        [
            pdflatex_path,
            "-interaction=nonstopmode",
            f"-output-directory={str(path.parent)}",
            str(path),
        ],
        stdout=subprocess.DEVNULL,
    )
    pdf = str(path.with_suffix(".pdf"))
    png = str(path.with_suffix(".png"))
    subprocess.call(
        [
            imagemagick_convert_path,
            "-density",
            "1200",
            "-sharpen",
            "0x1.0",
            "-quality",
            "100",
            "-background",
            "white",
            "-alpha",
            "remove",
            "-alpha",
            "off",
            "-resize",
            "25%",
            pdf,
            png,
        ],
        stdout=subprocess.DEVNULL,
    )

    for suffix in [".pdf", ".aux", ".log", ".tex"]:
        path.with_suffix(suffix).unlink()


def make_animation(output_file: Path, input_dir: Path):
    subprocess.call(
        [
            imagemagick_convert_path,
            "-dispose",
            "previous",
            "-delay",
            "100",
            str(input_dir / "*.png"),
            "-loop",
            "0",
            str(output_file),
        ],
        stdout=subprocess.DEVNULL,
    )
