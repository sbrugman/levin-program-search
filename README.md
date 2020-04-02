## Python Implementation

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black) 
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/download/releases/3.6.0/)

This section is meant to give an overview of design decisions for practical implementation of the theory provided above.
It is build up in the following way: we start off with a naive implementation and then optimize this in later subsections.

### Code
The code accompanying this subsection can be found [here](https://github.com/sbrugman/levin-program-search/tree/master/implementations/).

Design decisions:
- Ordering or program enumeration (lexicographic)
- Programs that halted do not benefit from longer run times, only consider programs with runtime limit.
- Profile ([short circuit of array equality](https://stackoverflow.com/questions/26260848/numpy-fast-check-for-complete-array-equality-like-matlabs-isequal))

### Installation

Python requirements: `pip install -r requirements.txt`

For generating images and animations:
- imagemagick: https://imagemagick.org/script/download.php
- pdflatex: https://miktex.org/download
- ghostscript: https://www.ghostscript.com/download/gsdnld.html
- update `config.py` with the paths

### Functionality

#### Deterministic Levin Search

```
usage: levin_search.py [-h] [--version] [--work_tape_size WORK_TAPE_SIZE]
                       [--program_tape_size PROGRAM_TAPE_SIZE]
                       [--primitives_set {DEFAULT,WEIGHT}]
                       [--search_log SEARCH_LOG]
                       [--solutions_file SOLUTIONS_FILE]
                       {POSITION,COUNT,EVEN,ODD,FIZZ,FIZZ_COMPLETE,BUZZ,BUZZ_COMPLETE,FIZZBUZZ,FIZZBUZZ_COMPLETE,NEGATIVE_ONE,NEGATIVE_ONE_TWO_THREE}
                       search_length solutions_dir

Levin search for Discovering Low Complexity Neural Network Weights

positional arguments:
  {POSITION,COUNT,EVEN,ODD,FIZZ,FIZZ_COMPLETE,BUZZ,BUZZ_COMPLETE,FIZZBUZZ,FIZZBUZZ_COMPLETE,NEGATIVE_ONE,NEGATIVE_ONE_TWO_THREE}
                        Which task to run? Tasks can be defined in `task.py`
  search_length         Search for programs up to this length.
  solutions_dir         Directory to store solutions, created if not exists

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --work_tape_size WORK_TAPE_SIZE
                        The size of the work tape
  --program_tape_size PROGRAM_TAPE_SIZE
                        The size of the program tape
  --primitives_set {DEFAULT,WEIGHT}
                        Use the following set of primitives
  --search_log SEARCH_LOG
                        Store the log of the deterministic levin search
                        process (.csv).
  --solutions_file SOLUTIONS_FILE
                        Store the solutions found in this file (.json)
```

Example usage Count task:

```console
python levin_search.py COUNT 4
```

#### Run a program

```
usage: run_program.py [-h] [--version] [--work_tape_size WORK_TAPE_SIZE]
                      [--program_tape_size PROGRAM_TAPE_SIZE]
                      [--n_weights N_WEIGHTS]
                      [--primitives_set {DEFAULT,WEIGHT}]
                      {file,string} ... log_file

Program Running for Discovering Low Complexity Neural Network Weights

positional arguments:
  {file,string}
  log_file              Store the logs in this file (.jsonl)

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --work_tape_size WORK_TAPE_SIZE
                        The size of the work tape
  --program_tape_size PROGRAM_TAPE_SIZE
                        The size of the program tape
  --n_weights N_WEIGHTS
                        The number of weights
  --primitives_set {DEFAULT,WEIGHT}
                        Use the following set of primitives
```

Example to run from file:

```console
python run_program.py file program_file.txt program_log.jsonl
```

Example to run from command line string:

```console
python run_program.py string 1,0,2,0 program_log.jsonl
```

#### Convert program to table or animation

```
usage: program_convert.py [-h] [--version] [--work_tape_size WORK_TAPE_SIZE]
                          [--program_tape_size PROGRAM_TAPE_SIZE]
                          program_file {table,animation} ...

Levin search for Discovering Low Complexity Neural Network Weights

positional arguments:
  program_file          Which log file to use?
  {table,animation}
    table               Table with the program instructions
    animation           Animate the program run

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --work_tape_size WORK_TAPE_SIZE
                        The size of the work tape
  --program_tape_size PROGRAM_TAPE_SIZE
                        The size of the program tape
```

Example usage for generating a table:

```console
python program_convert.py program_file.jsonl table program_table.md
```

Example usage for generating an animation:

```console
python program_convert.py program_file.jsonl animation animation.gif
```
