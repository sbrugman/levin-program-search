"""Primitives for an universal computer as described in section 4.3. The machine consists of 13 operations. Notable
are the limitations in the interaction with the environment, which is implemented marginally. The instruction
`get_input` always provides a zero. The `output` instruction outputs to the current weight pointer, which is then
increased, which does not allow to control the weight pointer. The WeightPrimitives take a more sophisticated
approach towards interaction with the environment. """
import itertools
from typing import Sequence

from halt import HaltingCode
from primitives import Primitives
from program import Program


class InitialPrimitives(Primitives):
    def __init__(self):
        op_args = [3, 1, 1, 0, 3, 2, 2, 1, 1, 1, 3, 3, 1]
        super().__init__(op_args)

    def args_generator(self, state: Program, op_id: int):
        n_args = self.get_n_args(op_id)
        # Syntactically valid ranges
        jump_range = range(state.min, state.max + 1 + 1 + n_args + 1)
        content_range = range(state.min, state.max + 1 + n_args + 1)

        if abs(state.min) >= state.work_tape_size:
            allocate_range = None
        else:
            allocate_range = (
                range(1, min(5, state.work_tape_size - abs(state.min)) + 1),
            )

        if state.min == 0:
            free_range = None
        else:
            free_range = (range(1, min(abs(state.min), 5) + 1),)

        write_range = range(state.min, -1 + 1)
        get_input_range = range(19 + 1)

        op_args = [
            (content_range, content_range, jump_range),
            (content_range,),
            (jump_range,),
            [],
            (content_range, content_range, write_range),
            (get_input_range, write_range),
            (content_range, write_range),
            allocate_range,
            (write_range,),
            (write_range,),
            (content_range, content_range, write_range),
            (content_range, content_range, write_range),
            free_range,
        ]

        return Primitives._generator(op_args, op_id)

    def get_op_names(self) -> Sequence[str]:
        return [
            "JUMPLEQ",
            "OUTPUT",
            "JUMP",
            "STOP",
            "ADD",
            "GET_INPUT",
            "MOVE",
            "ALLOCATE",
            "INCREMENT",
            "DECREMENT",
            "SUBTRACT",
            "MULTIPLY",
            "FREE",
        ]

    @staticmethod
    def run_op(op_id: int, state: Program, args):
        """Given a operator ID, return the operator and its number of arguments.

        Args:
            op_id: The operator ID
            state: the state
            args: the operation arguments

        Returns:
            A tuple with the operator in combination with its number of arguments.
        """
        ops = [
            Primitives.jumpleq,
            Primitives.output,
            Primitives.jump,
            Primitives.stop,
            Primitives.add,
            Primitives.get_input,
            Primitives.move,
            Primitives.allocate,
            Primitives.increment,
            Primitives.decrement,
            Primitives.subtract,
            Primitives.multiply,
            Primitives.free,
        ]

        try:
            ops[op_id](state, *args)
        except IndexError:
            state.halt = HaltingCode.ERROR_INSTRUCTION_OUT_OF_SET
            return
