import attr


@attr.s(slots=True)
class SearchState(object):
    logger = attr.ib(repr=False)
    n_runs = attr.ib(default=0, converter=int)
    n_steps = attr.ib(default=0, converter=int)
    space_size = attr.ib(default=0, converter=int)
    phase = attr.ib(default=0, converter=int)
    solutions = attr.ib(factory=list)
    # Programs that HALTED and hence do not benefit from longer run times
    memory = attr.ib(factory=list, repr=False)
