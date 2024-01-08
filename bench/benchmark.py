# todo combine benchmarks of scorers into common code base
from __future__ import annotations

import timeit

import pandas as pd


def benchmark(name, func, setup, lengths, count):
    print(f"starting {name}")
    start = timeit.default_timer()
    results = []
    for length in lengths:
        test = timeit.Timer(func, setup=setup.format(length, count))
        results.append(min(test.timeit(number=1) for _ in range(7)) / count)
    stop = timeit.default_timer()
    print(f"finished {name}, Runtime: ", stop - start)
    return results


setup = """
from difflib import SequenceMatcher
from cydifflib import SequenceMatcher as CySequenceMatcher
from cdifflib import CSequenceMatcher
import string
import random
random.seed(18)
characters = string.ascii_letters + string.digits + string.whitespace + string.punctuation
a      = ''.join(random.choice(characters) for _ in range({0}))
b_list = [''.join(random.choice(characters) for _ in range({0})) for _ in range({1})]
"""

lengths = list(range(1, 128, 2))
count = 2000

time_difflib = benchmark(
    "difflib",
    "[SequenceMatcher(None, a, b).get_matching_blocks() for b in b_list]",
    setup,
    lengths,
    count,
)

time_cdifflib = benchmark(
    "cdifflib",
    "[CSequenceMatcher(None, a, b).get_matching_blocks() for b in b_list]",
    setup,
    lengths,
    count,
)

time_cydifflib = benchmark(
    "cydifflib",
    "[CySequenceMatcher(None, a, b).get_matching_blocks() for b in b_list]",
    setup,
    lengths,
    count,
)


results = pd.DataFrame(
    data={
        "length": lengths,
        "difflib": time_difflib,
        "cdifflib": time_cdifflib,
        "cydifflib": time_cydifflib,
    }
)

results.to_csv("benchmark_results.csv", sep=",", index=False)
