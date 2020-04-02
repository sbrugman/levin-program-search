from pathlib import Path

import attr
from tqdm import tqdm
import numpy as np

from halt import HaltingCode
from logs import get_logger
from search_state import SearchState
from solution import Solution
from task import Task, Tasks
from universal_machine import UniversalMachine
from primitives import Primitives
from program import Program


def run_program(
    program: list,
    current_time_limit: int,
    universal_machine: UniversalMachine,
    base_program: Program,
    log_file: Path = None,
):
    state = attr.evolve(
        base_program,
        program_tape=program,
        weights=np.zeros(base_program.n_weights, dtype=np.int16),
        work_tape=[],
    )
    universal_machine.run(state, current_time_limit, log_file)

    return state


def levin_search_phase(
    search_state: SearchState,
    program_trail_status: Program,
    program_trail_program: list,
    universal_machine: UniversalMachine,
    task: Task,
    base_program: Program,
    depth: int = 0,
):
    phase_space_size = 0

    # Add the primitives ordered by their length (ascending)
    for instruction in universal_machine.primitives.ops_ordered:
        # The length of the new program
        new_program_length = (
            program_trail_status.oracle_address
            + universal_machine.primitives.op_args[instruction]
            + 1
        )

        # The generated program is longer than the current maximum length
        if new_program_length > search_state.phase:
            continue

        # 2^phase * 2^(-program_length) (+ 2^9)
        time_limit = 2 ** (search_state.phase + -1 * new_program_length + 9)

        for args in universal_machine.primitives.args_generator(
            program_trail_status, instruction,
        ):
            # Create the new program
            program = program_trail_program.copy()
            program.extend((instruction,) + args)

            if program in search_state.memory:
                continue

            status = run_program(program, time_limit, universal_machine, base_program)

            search_state.logger.debug(
                f"{program};{status.halt.name};{time_limit};{search_state.phase}"
            )

            if status.halt == HaltingCode.CONTINUE:
                # Append another instruction!
                levin_search_phase(
                    search_state,
                    status,
                    program,
                    universal_machine,
                    task,
                    base_program,
                    depth + 1,
                )
            else:
                phase_space_size += 1

                search_state.n_runs += 1
                search_state.n_steps += status.current_runtime

                if status.halt not in [HaltingCode.ERROR_CURRENT_TIME_LIMIT]:
                    search_state.memory.append(program)

                # Solutions come in here
                if task.eval_program_samples(status.weights):
                    search_state.solutions.append(
                        Solution(
                            program=program,
                            found_after=search_state.n_runs,
                            time_limit=time_limit,
                            current_runtime=status.current_runtime,
                            phase=search_state.phase,
                            generalizes=task.eval_program(status.weights),
                            complexity=len(program) + np.log(status.current_runtime),
                        )
                    )

    search_state.space_size += phase_space_size

    if depth == 0:
        search_state.solutions = [
            attr.evolve(k, space_size=search_state.space_size)
            for k in search_state.solutions
        ]


def main_run_program(
    primitives: Primitives,
    program: list,
    program_tape_size: int,
    work_tape_size: int,
    n_weights: int,
    log_file: Path,
    maxint: int = 10000,
    current_runtime: int = 2 ** 20,
):
    universal_machine = UniversalMachine(primitives)

    # Base program
    base_program = Program(
        program_tape_size=program_tape_size,
        work_tape_size=work_tape_size,
        n_weights=n_weights,
        maxint=maxint,
    )

    return run_program(
        program, current_runtime, universal_machine, base_program, log_file
    )


def main_levin_search(
    task: Tasks,
    primitives: Primitives,
    work_tape_size: int = 1000,
    program_tape_size: int = 100,
    search_length: int = 8,
    n_weights: int = 100,
    maxint: int = 10000,
    search_log_file: Path = None,
):
    task = Task(task=task)
    universal_machine = UniversalMachine(primitives)

    initial_program_tape = []
    initial_runtime_limit = 2

    base_program = Program(
        program_tape_size=program_tape_size,
        work_tape_size=work_tape_size,
        n_weights=n_weights,
        maxint=maxint,
    )

    program = run_program(
        initial_program_tape, initial_runtime_limit, universal_machine, base_program
    )

    logger = get_logger("levin_search", search_log_file)
    logger.debug("Program;Halting Status;Current Runtime Limit;Phase")

    search_state = SearchState(logger)
    for search_state.phase in tqdm(
        range(1, search_length + 1), desc=f"Levin search for task {task.task}"
    ):
        levin_search_phase(
            search_state,
            program,
            initial_program_tape,
            universal_machine,
            task,
            base_program,
        )

    return search_state
