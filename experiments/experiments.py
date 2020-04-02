import json
import logging
import sys
from pathlib import Path
from typing import List

from jinja2.environment import Template

sys.path.insert(0, r"../implementation/")

from console.levin_search import main as levin_search
from console.run_program import main as run_program
from console.program_convert import main as program_convert
from console.utils import program_format
from paths import experiments_dir, logs_dir, root_dir


exp_logger = logging.getLogger("experiment")
exp_logger.setLevel(logging.INFO)


def generate_solution_stub(metrics, task, table, output_file: Path):
    exp_logger.info(f"Generate SOLUTION for {metrics}")
    content = (experiments_dir() / "SOLUTION.md.jinja").read_text()
    template = Template(content)
    stub = template.render(
        program=str(metrics["program"]),
        program_length=len(metrics["program"]),
        program_clean=program_format(metrics["program"], "_"),
        program_comma=program_format(metrics["program"], ","),
        task=task,
        table=table,
        n_runs=metrics["found_after"],
        runtime=metrics["current_runtime"],
        runtime_limit=metrics["time_limit"],
        space_probability=f"$$\\frac{{1}}{{{metrics['space_size']}}}$$",
        complexity=metrics["complexity"]
    )
    output_file.write_text(stub)


def generate_search_stub(
    task, solutions, stats: dict, search_length: int, output_file: Path
):
    content = (experiments_dir() / "SEARCH.md.jinja").read_text()
    template = Template(content)
    stub = template.render(
        task=task,
        search_length=search_length,
        n_runs=stats["n_runs"],
        n_steps=stats["n_steps"],
        solutions=solutions,
        n_generalizes=stats["n_generalizes"],
        n_solutions=stats["n_solutions"],
    )
    output_file.write_text(stub)


def generate_task_stub(
    task: str,
    search_stub: str,
    solution_stubs: List[str],
    output_file: Path,
):
    content = (experiments_dir() / "TASK.md.jinja").read_text()
    template = Template(content)
    stub = template.render(
        task=task, search_stub=search_stub, solution_stubs=solution_stubs
    )
    output_file.write_text(stub)


def main(task, search_length, primitives="DEFAULT"):
    # For each task
    exp_logger.info("Generate directories")
    task_dir = logs_dir() / f"{task}_{primitives.lower()}"
    task_dir.mkdir(exist_ok=True, parents=True)

    images_dir = root_dir() / "blog" / "images"
    image_task_dir = images_dir / task
    image_task_dir.mkdir(exist_ok=True)

    exp_logger.info("Levin search")
    levin_search(
        [
            "--primitives_set",
            primitives,
            task.upper(),
            str(search_length),
            str(task_dir),
            "--search_log",
            str(task_dir / "search.csv"),
        ]
    )

    # For each solution
    solutions = []
    total = 0
    generalizes = 0
    for solution_file in task_dir.glob("phase*.json"):
        metrics_file = solution_file.read_text()
        metrics = json.loads(metrics_file)

        total += 1
        if not metrics["generalizes"]:
            continue

        generalizes += 1

        program = metrics["program"]
        solutions.append(program)

        exp_logger.info(f"Run program {solution_file}")
        run_program(
            [
                "--primitives_set",
                primitives,
                "string",
                program_format(program, ","),
                str(solution_file.with_suffix(".jsonl")),
            ]
        )

        exp_logger.info(f"Generate table {solution_file}")
        program_convert(
            [
                str(solution_file.with_suffix(".jsonl")),
                "table",
                "--primitives_set",
                primitives,
                str(solution_file.with_suffix(".table.md")),
            ]
        )

        exp_logger.info(f"Generate animation {solution_file}")
        program_convert(
            [
                str(solution_file.with_suffix(".jsonl")),
                "animation",
                str(image_task_dir / f"animation_{program_format(program, '_')}.gif"),
            ]
        )

        table = solution_file.with_suffix(".table.md").read_text()

        exp_logger.info(f"Generate solution stub {solution_file}")
        generate_solution_stub(
            metrics, task, table, solution_file.with_suffix(".solution.md")
        )

    with (task_dir / "search.json").open() as f:
        stats = json.load(f)
    stats["n_solutions"] = total
    stats["n_generalizes"] = generalizes

    exp_logger.info(f"Generate search stub")
    generate_search_stub(task, solutions, stats, search_length, task_dir / "search.md")
    search_stub = (task_dir / "search.md").read_text()

    exp_logger.info(f"Generate task stub")
    task_stub = task_dir / "task.md"
    generate_task_stub(
        task.capitalize(),
        search_stub,
        [p.read_text() for p in task_dir.glob("*.solution.md")],
        task_stub,
    )


if __name__ == "__main__":
    main(task="count", search_length=4)
    main(task="position", search_length=8) # includes 2^9
    main(task="position", search_length=9, primitives="WEIGHT") # includes 2^9 bonus

    main(task="odd", search_length=6)
    main(task="even", search_length=8)
    main(task="fizz", search_length=10)
    main(task="negative_one", search_length=8)
