import pytest
import numpy as np

from halt import HaltingCode
from primitives import Primitives
from program import Program


@pytest.fixture(scope="session")
def primitives():
    return Primitives


def test_jumpleq_equal(primitives, jump_to=5):
    state = Program(program_tape=[1, 1, 1, 1, 3, 3, 3])
    primitives.jumpleq(state, 0, 1, jump_to)
    assert state.instruction_pointer == jump_to
    assert state.jumped


def test_jumpleq_equal_out_of_bounds(primitives, jump_to=15):
    state = Program(program_tape=[1, 1, 1, 1, 3, 3, 3])
    primitives.jumpleq(state, 0, 1, jump_to)

    assert state.halt == HaltingCode.ERROR_INVALID_JUMP


def test_jumpleq_greater(primitives, before=3, jump_to=5):
    state = Program(program_tape=[2, 1, 1, 1, 3, 3, 3], instruction_pointer=before)
    primitives.jumpleq(state, 0, 1, jump_to)
    assert state.instruction_pointer == before
    assert not state.jumped


def test_jumpleq_less(primitives, jump_to=5):
    state = Program(program_tape=[0, 1, 1, 1, 3, 3, 3])
    primitives.jumpleq(state, 0, 1, jump_to)
    assert state.instruction_pointer == jump_to
    assert state.jumped


def test_jump(primitives, jump_to=4):
    state = Program(program_tape=[1, 1, 1, 1, 3, 3, 3])
    primitives.jump(state, jump_to)
    assert state.instruction_pointer == jump_to
    assert state.jumped


def test_jump_out_of_bounds(primitives, jump_to=10):
    state = Program(program_tape=[1, 1, 1, 1, 3, 3, 3])
    primitives.jump(state, jump_to)
    assert state.halt == HaltingCode.ERROR_INVALID_JUMP


def test_read_weight(primitives):
    state = Program(
        program_tape=[-1, 5],
        work_tape=[0],
        min=-1,
        n_weights=10,
        weights=np.arange(1, 11, 1, dtype=np.int16),
    )
    primitives.read_weight(state, 0, 1)
    assert state.work_tape == [5]


def test_read_weight_index_lower(primitives):
    state = Program(
        program_tape=[-1, 0],
        work_tape=[0],
        min=-1,
        n_weights=10,
        weights=np.arange(1, 11, 1, dtype=np.int16),
    )
    primitives.read_weight(state, 0, 1)
    assert state.halt == HaltingCode.ERROR_WEIGHT_POINTER_OUT_BOUNDS


def test_read_weight_index_upper(primitives):
    state = Program(
        program_tape=[-1, 10],
        work_tape=[0],
        min=-1,
        n_weights=10,
        weights=np.arange(1, 11, 1, dtype=np.int16),
    )
    primitives.read_weight(state, 0, 1)
    assert state.halt is None


def test_write_weight(primitives):
    state = Program(
        program_tape=[5, 1337],
        work_tape=[0],
        min=-1,
        n_weights=10,
        weights=np.arange(1, 11, 1, dtype=np.int16),
    )
    primitives.write_weight(state, 1, 0)
    assert state.weights.tolist() == [1, 2, 3, 4, 1337, 6, 7, 8, 9, 10]


def test_free_lower_bound(primitives):
    state = Program(program_tape=[0, 1, 2, 3], work_tape=[1, 2], min=-2)
    primitives.free(state, 0)
    assert state.halt == HaltingCode.ERROR_FREE_OUT_BOUNDS


def test_free_upper_bound(primitives):
    state = Program(program_tape=[0, 1, 2, 3], work_tape=[1, 2], min=-2)
    primitives.free(state, 6)
    assert state.halt == HaltingCode.ERROR_FREE_OUT_BOUNDS


def test_free(primitives):
    state = Program(program_tape=[0, 1, 2, 3], work_tape=[1, 2], min=-2)
    primitives.free(state, 2)
    assert state.halt is None
    assert state.work_tape == []


def test_free_too_much(primitives):
    state = Program(program_tape=[0, 1, 2, 3], work_tape=[1, 2], min=-2)
    primitives.free(state, 3)
    assert state.halt == HaltingCode.ERROR_FREE_OUT_BOUNDS


def test_increment_invalid(primitives):
    state = Program(program_tape=[0, 1, 2, 3], work_tape=[1, 2], min=-2)
    primitives.increment(state, 1)
    assert state.halt == HaltingCode.ERROR_ILLEGAL_WRITE


def test_increment(primitives):
    state = Program(program_tape=[0, 1, 2, 3], work_tape=[1, 2], min=-2)
    primitives.increment(state, -2)
    assert state.halt is None
    assert state.work_tape == [1, 3]


def test_increment_2(primitives):
    state = Program(program_tape=[0, 1, 2, 3], work_tape=[1, 2], min=-2)
    primitives.increment(state, -1)
    assert state.halt is None
    assert state.work_tape == [2, 2]

