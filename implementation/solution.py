import attr


@attr.s(slots=True)
class Solution(object):
    program = attr.ib(type=list)
    found_after = attr.ib(convert=int)
    time_limit = attr.ib(convert=int)
    current_runtime = attr.ib(convert=int)
    phase = attr.ib(convert=int)
    space_size = attr.ib(default=None)
    generalizes = attr.ib(default=False, type=bool)
    complexity = attr.ib(default=None, type=float)

