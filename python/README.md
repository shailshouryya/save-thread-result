# save-thread-result Python API

<p align="center">
  <a href="https://github.com/Shail-Shouryya/save-thread-result/blob/main/LICENSE"><img alt="GitHub license" src="https://img.shields.io/github/license/Shail-Shouryya/save-thread-result?color=yellow&labelColor=black"></a>
  <a href="https://docs.python.org/3/index.html">    <img src="https://img.shields.io/badge/python-3.6%2B-blue?labelColor=black"/></a>
  <a href="https://www.python.org/dev/peps/pep-0008"><img src="https://img.shields.io/badge/code%20style-PEP8-yellow.svg?labelColor=black"/></a>
  <a href="https://github.com/Shail-Shouryya/save-thread-result/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/Shail-Shouryya/save-thread-result?color=blue&labelColor=black"></a>
  <a href="https://github.com/Shail-Shouryya/save-thread-result/network"><img alt="GitHub forks" src="https://img.shields.io/github/forks/Shail-Shouryya/save-thread-result?color=yellow&labelColor=black"></a>
  <br>
  <a href="https://badge.fury.io/py/save-thread-result"><img src="https://badge.fury.io/py/save-thread-result.svg" alt="PyPI version" height="20"></a>
  <br>
  <a href="https://pypi.org/project/save-thread-result/"><img alt="PyPI - Wheel" src="https://img.shields.io/pypi/wheel/save-thread-result?labelColor=black&label=PyPI%20-%20Wheel"></a>
  <a href="https://pypi.org/project/save-thread-result/#files/"><img alt="PyPI - Format" src="https://img.shields.io/pypi/format/save-thread-result?labelColor=black&label=PyPI%20-%20Format"></a>
  <a href="https://pypi.org/project/save-thread-result/#history/"><img alt="PyPI - Status" src="https://img.shields.io/pypi/status/save-thread-result?labelColor=black&label=PyPI%20-%20Status"></a>
  <br>
  <a href="https://pypi.org/project/save-thread-result/"><img alt="PyPI - Implementation" src="https://img.shields.io/pypi/implementation/save-thread-result?labelColor=black&label=PyPI%20-%20Implementation"></a>
  <a href="https://pypi.org/project/save-thread-result/"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/save-thread-result?labelColor=black&label=PyPI%20-%20Python%20Version"></a>
  <br>
  <a href="https://codebeat.co/projects/github-com-shail-shouryya-save-thread-result-main"><img alt="codebeat badge" src="https://codebeat.co/badges/a0678ef2-391a-4aee-82bf-cf223c4084ce" /></a>
</p>

<details>
  <summary><b>Installing the package</b></summary>

Enter the following in your command line:

```python
# if something isn't working properly, try rerunning this
# the problem may have been fixed with a newer version

pip3 install -U save-thread-result     # MacOS/Linux
pip  install -U save-thread-result     # Windows
```
</details>

<details>
  <summary><b>Initializing the <code>ThreadWithResult</code> class</b></summary>

This package uses a `threading.Thread` subclass `ThreadWithResult` that saves the result of a thread (from `threading` built-in package in Python Standard library) as its `result` attribute - i.e. after the thread finishes running, call `thread.result` to get the return value from the function that ran on that thread.

```
python3     # MacOS/Linux
python      # Windows
```
```python
from save_thread_result import ThreadWithResult

thread = ThreadWithResult(
    target = my_function,
    args   = (my_function_arg1, my_function_arg2, ...)
    kwargs = (my_function_kwarg1=kwarg1_value, my_function_kwarg2=kwarg2_value, ...)
)

thread.start()
thread.join()
if getattr(test_case_thread_1, 'result', None):
    print(thread.result)
else:
    print('ERROR! Something went wrong while executing this thread, and the function you passed in did NOT complete!!')
```

</details>

<details>
  <summary><b>Seeing <b>all</b> available methods and attributes for `ThreadWithResult` class</b></summary>

```
python3     # MacOS/Linux
python      # Windows
```
```python
from save_thread_result import ThreadWithResult

help(ThreadWithResult)
```

</details>

<details>
  <summary><b>Usage Statistics</b></summary>

- [PePy](https://pepy.tech/project/save-thread-result)
- [PyPi Stats](https://pypistats.org/packages/save-thread-result)
</details>
<p>
  <a href="https://pypistats.org/packages/save-thread-result"><img alt="PyPI - Daily Downloads" src="https://img.shields.io/pypi/dd/save-thread-result?labelColor=black&color=blue&label=PyPI%20downloads"></a>
  <br>
  <a href="https://pypistats.org/packages/save-thread-result"><img alt="PyPI - Weekly Downloads" src="https://img.shields.io/pypi/dw/save-thread-result?labelColor=black&color=yellow&label=PyPI%20downloads"></a>
  <a href="https://pepy.tech/project/save-thread-result"><img alt="PePY Weekly Downloads" src="https://static.pepy.tech/personalized-badge/save-thread-result?period=week&units=international_system&left_color=black&right_color=blue&left_text=PePY%20Downloads/week"></a>
  <br>
  <a href="https://pypistats.org/packages/save-thread-result"><img alt="PyPI - Monthly Downloads" src="https://img.shields.io/pypi/dm/save-thread-result?labelColor=black&color=blue&label=PyPI%20downloads"></a>
  <a href="https://pepy.tech/project/save-thread-result"><img alt="PePY Monthly Downloads" src="https://static.pepy.tech/personalized-badge/save-thread-result?period=month&units=international_system&left_color=black&right_color=yellow&left_text=PePY%20Downloads/month"></a>
  <br>
  <a href="https://pepy.tech/project/save-thread-result"><img alt="PePY Total Downloads" src="https://static.pepy.tech/personalized-badge/save-thread-result?period=total&units=international_system&left_color=black&right_color=yellow&left_text=PePY%20Downloads%20Total"></a>
</p>
