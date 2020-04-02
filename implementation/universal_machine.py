"""Discovering neural networks."""
from halt import HaltingCode
from logs import get_logger


class UniversalMachine(object):
    """
    Universal Machine
    """

    def __init__(self, primitives):
        self.primitives = primitives

    def _run_operation(self, state, current_time_limit, op_code):
        if not (0 <= op_code < self.primitives.n_ops):
            state.halt = HaltingCode.ERROR_INSTRUCTION_OUT_OF_SET
            return

        if (
            state.instruction_pointer + self.primitives.get_n_args(op_code)
        ) > state.max:
            state.halt = HaltingCode.ERROR_INVALID_INSTRUCTION_POINTER
            return

        args_contents = [
            state.read(state, state.instruction_pointer + i + 1)
            for i in range(self.primitives.get_n_args(op_code))
        ]
        if state.halt is not None:
            return

        state.current_runtime += 1
        self.primitives.run_op(op_code, state, args_contents)
        if state.halt:
            return

        if not state.jumped:
            state.instruction_pointer += 1 + self.primitives.get_n_args(op_code)
        else:
            state.jumped = False

        if state.current_runtime >= current_time_limit:
            state.halt = HaltingCode.ERROR_CURRENT_TIME_LIMIT
            return

    def run(self, state, current_time_limit, log_file=None):
        logger = get_logger("universal_machine", log_file)

        while True:
            logger.debug(state.to_json())

            if state.instruction_pointer == state.oracle_address:
                state.halt = HaltingCode.CONTINUE
                return

            op_code = state.read(state, state.instruction_pointer)
            if state.halt is not None:
                return

            self._run_operation(state, current_time_limit, op_code)
