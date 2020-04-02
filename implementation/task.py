from enum import Enum, auto

import numpy as np


class Tasks(Enum):
    # Because we believe in credit assignment: https://stackoverflow.com/a/46385352/470433

    POSITION = auto()
    COUNT = auto()
    EVEN = auto()
    ODD = auto()
    FIZZ = auto()
    FIZZ_COMPLETE = auto()
    BUZZ = auto()
    BUZZ_COMPLETE = auto()
    FIZZBUZZ = auto()
    FIZZBUZZ_COMPLETE = auto()
    NEGATIVE_ONE = auto()
    NEGATIVE_ONE_TWO_THREE = auto()

    def __str__(self):
        return self.name

    @staticmethod
    def from_string(s):
        try:
            return Tasks[s]
        except KeyError:
            raise ValueError()


def short_circuit_check(a, b, n=10):
    L = int(len(a) / n)
    for i in range(n):
        j = i * L
        if not all(a[j : j + L] == b[j : j + L]):
            return False
    return True


class Task(object):
    def __init__(self, task: Tasks, size: int = 100):
        self.task = task

        if task == Tasks.POSITION:
            self.solution = np.array(list(range(1, size + 1)), dtype=np.int16)
        elif task == Tasks.COUNT:
            self.solution = np.ones(size, dtype=np.int16)
        elif task == Tasks.EVEN:
            self.solution = np.array(
                [int(x % 2 == 0) * 1 for x in range(1, size + 1)], dtype=np.int16
            )
        elif task == Tasks.ODD:
            self.solution = np.array(
                [int((x + 1) % 2 == 0) * 1 for x in range(1, size + 1)], dtype=np.int16
            )
        elif task == Tasks.FIZZ:
            self.solution = np.array(
                [int(x % 3 == 0) * 1 for x in range(1, size + 1)], dtype=np.int16
            )
        elif task == Tasks.FIZZ_COMPLETE:
            self.solution = np.array(
                [v if (v % 3) != 0 else -1 for v in range(1, size + 1)], dtype=np.int16
            )
        elif task == Tasks.BUZZ:
            self.solution = np.array(
                [int(x % 5 == 0) * 1 for x in range(1, size + 1)], dtype=np.int16
            )
        elif task == Tasks.BUZZ_COMPLETE:
            self.solution = np.array(
                [v if (v % 5) != 0 else -1 for v in range(1, size + 1)], dtype=np.int16
            )
        elif task == Tasks.FIZZBUZZ:
            self.solution = np.array(
                [int(x % 3 == 0) * 1 + int(x % 5 == 0) * 2 for x in range(1, size + 1)],
                dtype=np.int16,
            )
        elif task == Tasks.FIZZBUZZ_COMPLETE:
            self.solution = np.array(
                [
                    (int(x % 3 == 0) * 1 + int(x % 5 == 0) * 2) * -1
                    if (x % 3 == 0 or x % 5 == 0)
                    else x
                    for x in range(1, size + 1)
                ],
                dtype=np.int16,
            )
        elif task == Tasks.NEGATIVE_ONE:
            self.solution = np.ones(size, dtype=np.int16) * -1
        elif task == Tasks.NEGATIVE_ONE_TWO_THREE:
            self.solution = np.array([-1, -2, -3] * 33 + [-1], dtype=np.int16)
        else:
            raise ValueError(f"Task not supported '{task}'")

    def eval_program(self, solution):
        """Evaluate whether the solutions fully generalizes to the task.

        Args:
            solution: the predicted solution

        Returns:
            True if the solutions are equal
        """
        return short_circuit_check(solution, self.solution)

    def eval_program_samples(self, solution):
        """Evaluate whether the solution matches the three training examples for the task.

        Args:
            solution: the predicted solutions

        Returns:
            True if the solution matches all training samples
        """
        # Training examples (as in the paper)
        examples = [
            [5, 17, 86],
            [13, 55, 58],
            [40, 87, 94],
        ]

        for example in examples:
            if any(solution[example] != self.solution[example]):
                return False

        return True
