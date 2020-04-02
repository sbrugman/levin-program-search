from pathlib import Path


def root_dir():
    return Path(__file__).parent.parent.resolve()


def implementation_dir():
    return root_dir() / "implementation"


def experiments_dir():
    return root_dir() / "experiments"


def logs_dir():
    return root_dir() / "logs"
