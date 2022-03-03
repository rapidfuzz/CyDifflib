<h1 align="center">
 CyDifflib
</h1>
<p align="center">
  <a href="https://github.com/maxbachmann/CyDifflib/actions">
    <img src="https://github.com/maxbachmann/CyDifflib/workflows/Build/badge.svg"
         alt="Continous Integration">
  </a>
  <a href="https://pypi.org/project/cydifflib/">
    <img src="https://img.shields.io/pypi/v/cydifflib"
         alt="PyPI package version">
  </a>
  <a href="https://www.python.org">
    <img src="https://img.shields.io/pypi/pyversions/cydifflib"
         alt="Python versions">
  </a><br/>
  <a href="https://github.com/maxbachmann/CyDifflib/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/maxbachmann/CyDifflib"
         alt="GitHub license">
  </a>
</p>

<h4 align="center">CyDifflib is a fast implementation of difflib's algorithms, which can be used as a drop-in replacement</a>.</h4>


## 🚀 Benchmarks
The following benchmark compares the performance in the original difflib implementation, the library [cdifflib](https://github.com/mduggan/cdifflib) and CyDifflib

<p align="center">
<img src="https://raw.githubusercontent.com/maxbachmann/CyDifflib/main/bench/CyDifflib.svg?sanitize=true" alt="Benchmark CyDifflib">
</p>

## ⚙️ Installation

You can install this library from [PyPI](https://pypi.org/project/cydifflib/) with pip:
```
pip install cydifflib
```
CyDifflib provides binary wheels for all common platforms.

### Source builds

For a source build (for example from a SDist packaged) you only require a C++11 compatible compiler. You can install directly from GitHub if you would like.
```
pip install git+https://github.com/maxbachmann/CyDifflib.git@main
```

## 📖 Usage

The library can be used in the same way as difflib. Just use the `cydifflib` module instead of `difflib`:
```python
#from difflib import SequenceMatcher
from cydifflib import SequenceMatcher
```
The official [documentation of difflib](https://docs.python.org/3.10/library/difflib.html) explains how to use the library. If you work with a library which internally uses some of the algorithms of difflib it is possible to replace the implementation before importing this library. E.g. for `thefuzz` this can be done in the following way:
```python
from cydifflib import SequenceMatcher
import difflib

difflib.SequenceMatcher = SequenceMatcher
from thefuzz import fuzz
```

## 👍 Contributing

PRs are welcome!
- Found a bug? Report it in form of an [issue](https://github.com/maxbachmann/CyDifflib/issues). Any difference in behavior to difflib is considered as a bug.
- Can make something faster? Great! Just avoid external dependencies and remember that external behavior does not change.
- Have no time to code? Tell your friends and subscribers about CyDifflib.

Thank you :heart:

## ⚠️ License
Copyright 2021-present [Max Bachmann](https://github.com/maxbachmann). `CyDifflib` is free and open-source software licensed under the [MIT License](https://github.com/maxbachmann/CyDifflib/blob/main/LICENSE).
