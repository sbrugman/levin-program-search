from enum import Enum, auto, unique


@unique
class HaltingCode(Enum):
    """
    Halting codes for the Halting Exception
    """

    STOP = auto()
    ERROR_INVALID_INSTRUCTION_POINTER = auto()
    ERROR_CURRENT_TIME_LIMIT = auto()
    ERROR_INSTRUCTION_OUT_OF_SET = auto()
    ERROR_INVALID_JUMP = auto()
    ERROR_WEIGHT_SIZE_OUT_BOUNDS = auto()
    ERROR_WEIGHT_POINTER_OUT_BOUNDS = auto()
    ERROR_ILLEGAL_READ = auto()
    ERROR_ILLEGAL_WRITE = auto()
    ERROR_INPUT_OUT_BOUNDS = auto()
    ERROR_ALLOCATE_OUT_BOUNDS = auto()
    ERROR_FREE_OUT_BOUNDS = auto()
    ERROR_OVERFLOW = auto()
    CONTINUE = auto()
