"""Primitives for an universal computer as described in section 4.3. The machine consists of 13 operations. Notable
are the limitations in the interaction with the environment, which is implemented marginally. The instruction
`get_input` always provides a zero. The `output` instruction outputs to the current weight pointer, which is then
increased, which does not allow to control the weight pointer. The WeightPrimitives take a more sophisticated
approach towards interaction with the environment. """
import itertools
import math

import numpy as np

from halt import HaltingCode
from program import Program


class Primitives(object):
    def __init__(self, op_args):
        # Arg size per instruction
        self.op_args = np.array(op_args, dtype=np.int64)
        # Instructions ordered by arg size
        self.ops_ordered = np.argsort(self.op_args)
        # The number of operations
        self.n_ops = len(self.op_args)

    def get_n_args(self, op_id: int) -> int:
        """Get the number of arguments for an instruction

        Args:
            op_id: the instruction id

        Returns:
            The number of arguments
        """
        return self.op_args[int(op_id)]

    @staticmethod
    def jumpleq(state: Program, address1: int, address2: int, address3: int):
        """If Value in Address 1 <= Value in Address 2, Jump to Address 3

        Args:
            state: the program state
            address1: address 1
            address2: address 2
            address3: the address to jump to

        Notes:
            Rules for legal argument ranges and syntactical correctness:
            Jumps may lead to any address in the dynamic range [Min, Max + 1]
        """
        address1 = state.read(state, address1)
        if state.halt is not None:
            return

        address2 = state.read(state, address2)
        if state.halt is not None:
            return

        if address1 <= address2:
            Primitives.jump(state, address3)
            if state.halt is not None:
                return
        else:
            state.jumped = False

    @staticmethod
    def output(state: Program, address1: int):
        address1 = state.read(state, address1)
        if state.halt is not None:
            return

        if not (-10000 <= address1 <= 10000):
            state.halt = HaltingCode.ERROR_WEIGHT_SIZE_OUT_BOUNDS
            return

        try:
            state.weights[state.weight_pointer] = address1
        except IndexError:
            state.halt = HaltingCode.ERROR_WEIGHT_POINTER_OUT_BOUNDS
            return
        state.weight_pointer += 1

    @staticmethod
    def write_weight(state: Program, address1: int, address2: int):
        address1 = state.read(state, address1)
        if state.halt is not None:
            return

        address2 = state.read(state, address2) - 1
        if state.halt is not None:
            return

        if address2 < 0:
            state.halt = HaltingCode.ERROR_WEIGHT_POINTER_OUT_BOUNDS
            return

        if not (-10000 <= address1 <= 10000):
            state.halt = HaltingCode.ERROR_WEIGHT_SIZE_OUT_BOUNDS
            return

        try:
            state.weights[address2] = address1
        except IndexError:
            state.halt = HaltingCode.ERROR_WEIGHT_POINTER_OUT_BOUNDS
            return

    @staticmethod
    def read_weight(state: Program, address1: int, address2: int):
        address1 = state.read(state, address1)
        if state.halt is not None:
            return

        address2 = state.read(state, address2) - 1
        if state.halt is not None:
            return

        if address2 < 0:
            state.halt = HaltingCode.ERROR_WEIGHT_POINTER_OUT_BOUNDS
            return

        try:
            value = state.weights[address2]
        except IndexError:
            state.halt = HaltingCode.ERROR_WEIGHT_POINTER_OUT_BOUNDS
            return

        state.write(state, address1, value)
        if state.halt is not None:
            return

    @staticmethod
    def jump(state: Program, address1: int):
        """Jump to Address 1

        Args:
            state: the program state
            address1: address 1

        Notes:
            Rules for legal argument ranges and syntactical correctness.
            Jumps may lead to any address in the dynamic range [Min, Max + 1]

        """

        if not (state.min <= address1 <= state.oracle_address):
            state.halt = HaltingCode.ERROR_INVALID_JUMP
            return

        state.instruction_pointer = address1
        state.jumped = True

    @staticmethod
    def stop(state: Program):
        """Halt

        Args:
            state: the program state

        """
        state.halt = HaltingCode.STOP

    @staticmethod
    def add(state: Program, address1: int, address2: int, address3: int):
        address1 = state.read(state, address1)
        if state.halt is not None:
            return

        address2 = state.read(state, address2)
        if state.halt is not None:
            return

        state.write(state, address3, address1 + address2)
        if state.halt is not None:
            return

    @staticmethod
    def get_input(state: Program, address1: int, address2: int):
        """

        Args:
            state:
            address1:
            address2:

        Notes:
            GetInput reads the current value of the $i$th input field into address2, where $i$ is the value found in address1.

        """
        # equal to "set zero"
        if address1 >= 20:
            state.halt = HaltingCode.ERROR_INPUT_OUT_BOUNDS
            return

        state.write(state, address2, 0)
        if state.halt is not None:
            return

    @staticmethod
    def move(state: Program, address1: int, address2: int):
        address1 = state.read(state, address1)
        if state.halt is not None:
            return

        state.write(state, address2, address1)
        if state.halt is not None:
            return

    @staticmethod
    def allocate(state: Program, address1: int):
        # The size of the work tape is increased by the value found in address1
        # No more than 5 work tape cells may be Allocated or Freed at a time.
        # $Min$ is updated accordingly (growth beyond $-s_w$ halts the program).
        if (
            address1 > 5
            or address1 <= 0
            or -1 * (state.min - address1) > state.work_tape_size
        ):
            state.halt = HaltingCode.ERROR_ALLOCATE_OUT_BOUNDS
            return

        state.alloc(address1)

    @staticmethod
    def increment(state: Program, address1: int):
        # Operations that change the contents of certain cells may write only into work tape addresses in $[Min, -1]$.
        v1 = state.read(state, address1)
        if state.halt is not None:
            return

        state.write(state, address1, v1 + 1)
        if state.halt is not None:
            return

    @staticmethod
    def decrement(state: Program, address1: int):
        v1 = state.read(state, address1)
        if state.halt is not None:
            return

        state.write(state, address1, v1 - 1)
        if state.halt is not None:
            return

    @staticmethod
    def div(state: Program, address1: int, address2: int, address3: int):
        # Operations that change the contents of certain cells may write only into work tape addresses in $[Min, -1]$.
        address1 = state.read(state, address1)
        if state.halt is not None:
            return

        address2 = state.read(state, address2)
        if state.halt is not None:
            return

        try:
            state.write(state, address3, math.floor(address2 / address1))
            if state.halt is not None:
                return

        except OverflowError:
            state.halt = HaltingCode.ERROR_OVERFLOW
            return

    @staticmethod
    def subtract(state: Program, address1: int, address2: int, address3: int):
        # Operations that change the contents of certain cells may write only into work tape addresses in $[Min, -1]$.
        address1 = state.read(state, address1)
        if state.halt is not None:
            return

        address2 = state.read(state, address2)
        if state.halt is not None:
            return

        state.write(state, address3, address2 - address1)
        if state.halt is not None:
            return

    @staticmethod
    def multiply(state: Program, address1, address2, address3):
        # Operations that change the contents of certain cells may write only into work tape addresses in $[Min, -1]$.
        address1 = state.read(state, address1)
        if state.halt is not None:
            return

        address2 = state.read(state, address2)
        if state.halt is not None:
            return

        state.write(state, address3, address1 * address2)
        if state.halt is not None:
            return

    @staticmethod
    def free(state: Program, address1: int):
        # No more than 5 work tape cells may be Allocated or Freed at a time.
        if address1 > 5 or address1 <= 0 or (state.min + address1) > 0:
            state.halt = HaltingCode.ERROR_FREE_OUT_BOUNDS
            return

        state.free(address1)

    @classmethod
    def _generator(cls, op_args, op_id):
        try:
            args = op_args[op_id]
        except IndexError:
            raise ValueError("Operation not understood")

        if type(args) == list and not args:
            return [tuple()]
        if args is None:
            return []

        return list(itertools.product(*args))
