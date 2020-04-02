"""This file defines the State object."""
import json

import attr
import numpy as np

from halt import HaltingCode


@attr.s(slots=True)
class Program(object):
    program_tape_size = attr.ib(default=100)
    work_tape_size = attr.ib(default=10)
    maxint = attr.ib(default=10000)
    n_weights = attr.ib(default=100)
    halt = attr.ib(default=None)
    instruction_pointer = attr.ib(default=0)
    # -1 in the Jankowski paper, 0 in the Schmidhuber paper
    min = attr.ib(default=0)
    current_runtime = attr.ib(default=0)
    # Only used in combination with "output", "write_weight" replaces this
    weight_pointer = attr.ib(default=0)
    jumped = attr.ib(type=bool, default=False)
    weights = attr.ib(
        default=attr.Factory(
            lambda self: np.zeros(self.n_weights, dtype=np.int16), takes_self=True
        )
    )
    program_tape = attr.ib(factory=list)
    work_tape = attr.ib(factory=list)

    @program_tape.validator
    def check_program_tape(self, attribute, value):
        if len(value) > self.program_tape_size:
            raise ValueError("Program tape too long")

    @work_tape.validator
    def check_work_tape(self, attribute, value):
        if len(value) > self.work_tape_size:
            raise ValueError("Work tape exceeds limit")

    def alloc(self, i):
        """Allocate $$i$$ cells on the work tape

        Args:
            i: the number of cells to allocate
        """
        self.work_tape.extend([0] * i)
        self.min -= i

    def free(self, i):
        """Free $$i$$ cells on the work tape

        Args:
            i: the number of cells to free
        """
        self.work_tape = self.work_tape[:-i]
        self.min += i

    @property
    def max(self):
        """the maximum value property

        Notes:
            If $Max = -1$ then the current program is ``empty.''
        """
        return len(self.program_tape) - 1

    @property
    def oracle_address(self):
        """Defines the oracle address as a property, which is defined to be Max + 1.

        Returns:
            The oracle address.
        """
        return self.max + 1

    def to_json(self) -> str:
        """Encode the program in JSON

        Returns:
            JSON encoded object as string

        Notes:
            Could be replaced with `attr.asdict()`
        """
        data = {
            "state": {
                "min": int(self.min),
                "max": int(self.max),
                "halt": str(self.halt),
                "instruction_pointer": int(self.instruction_pointer),
                "current_runtime": int(self.current_runtime),
                "weight_pointer": int(self.weight_pointer),
            },
            "storage": {
                "program_tape": [int(c) for c in self.program_tape],
                "work_tape": [int(c) for c in self.work_tape],
                "weights": [int(w) for w in self.weights.tolist()],
            },
        }
        return json.dumps(data, separators=(",", ":"))

    def read(self, state, i):
        """Read from the tape.

        Args:
            i: Index of tape entry to read (note that work tape is indexed as negative numbers)

        Raises:
            Halt: reading an illegal position

        Returns:
            value of tape entry at index i
        """
        if not (self.min <= i <= self.max):
            state.halt = HaltingCode.ERROR_ILLEGAL_READ
            return

        if i < 0:
            return self.work_tape[abs(i) - 1]
        else:
            return self.program_tape[abs(i)]

    def write(self, state, i: int, value: int):
        """Writes to the tape.

        Args:
            i: Index of tape entry to write (note that work tape is indexed as negative numbers)
            value: The value to write at $$i$$.

        Notes:
            Results of arithmetic operations leading to underflow or overflow are replaced by -maxint or maxint, respectively.

        Raises:
            Halt: writing to an illegal position

        Returns:
            None
        """
        if not (self.min <= i <= -1):
            state.halt = HaltingCode.ERROR_ILLEGAL_WRITE
            return

        if value > self.maxint:
            value = self.maxint
        elif value < (-1 * self.maxint):
            value = -1 * self.maxint

        self.work_tape[abs(i) - 1] = value
