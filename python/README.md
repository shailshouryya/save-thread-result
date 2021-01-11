# save-thread-result Python API

<p align="center">
  <a href="https://github.com/Shail-Shouryya/save-thread-result/blob/main/LICENSE"><img alt="GitHub license" src="https://img.shields.io/github/license/Shail-Shouryya/save-thread-result?color=yellow&labelColor=black"></a>
  <a href="https://docs.python.org/3/index.html">    <img src="https://img.shields.io/badge/python-3-blue?labelColor=black"/></a>
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
  <summary><b>Motivation</b></summary>

I created this package because I needed to [store the result](https://github.com/Shail-Shouryya/yt_videos_list/commit/8fc62703047b9f8de287306239885cd5138a8d7e) of a thread [while running tests](https://github.com/Shail-Shouryya/yt_videos_list/blob/master/python/tests/test_shared.py) for the `yt_videos_list` package and there seemed to be no simple way to get the result from `threading.Thread()` without importing other modules, creating a `Queue`, or creating a `list` and then storing the result in the list, or doing other hacky things.
<details>
  <summary><b>Sources I looked at before creating the custom class below</b></summary>

- [Return value from thread](https://stackoverflow.com/questions/1886090/return-value-from-thread)
- [Threading in python: retrieve return value when using target= [duplicate]](https://stackoverflow.com/questions/2577233/threading-in-python-retrieve-return-value-when-using-target)
- [How to get the return value from a thread in python?](https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python_
- [Using Python Threading and Returning Multiple Results (Tutorial)](https://www.shanelynn.ie/using-python-threading-for-multiple-results-queue/)
- [How to get the return value from a thread using python](https://www.edureka.co/community/31966/how-to-get-the-return-value-from-a-thread-using-python)
- [How to manage python threads results?](https://stackoverflow.com/questions/3239617/how-to-manage-python-threads-results#3239815)
- [How to obtain the results from a pool of threads in python?](https://stackoverflow.com/questions/26104512/how-to-obtain-the-results-from-a-pool-of-threads-in-python)
- [Google search](https://www.google.com/search?hl=en&q=python%20save%20thread%20result)
</details>

<details>
  <summary><b>Implementation in <code>yt_videos_list</code></b></summary>

- see commits:
  - [Add custom class to store thread result](https://github.com/Shail-Shouryya/yt_videos_list/commit/8fc62703047b9f8de287306239885cd5138a8d7e)
  - [Make ThreadWithResult attribute names more descriptive](https://github.com/Shail-Shouryya/yt_videos_list/commit/f1d58f6deeb2becf9038a94c3fb964bccc5321d3)
  - [Add ThreadWithResult class docstring (test_shared.py)](https://github.com/Shail-Shouryya/yt_videos_list/commit/b10480b6979f96443ab9e2e62e515c4da30eccdb)
- see [Release 0.5.0](https://github.com/Shail-Shouryya/yt_videos_list/releases/tag/v0.5.0) for other threading bugs and workarounds!
</details>

This package is really only 6 lines of code:
```python
import threading

class ThreadWithResult(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None):
        def function():
            self.result = target(*args, **kwargs)
        super().__init__(group=group, target=function, name=name, daemon=daemon)
```

The explanation is in the [docstrings](https://github.com/Shail-Shouryya/save-thread-result/blob/main/python/save_thread_result/thread_with_result.py) in the `thread_with_result` submodule, and is also accessible through the python interpreter with
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
  <summary><b>Initializing and using the <code>ThreadWithResult</code> class</b></summary>

This package uses a `threading.Thread` subclass `ThreadWithResult` that saves the result of a thread (from `threading` built-in package in Python Standard library) as its `result` attribute - i.e. after the thread finishes running, call `thread.result` to get the return value from the function that ran on that thread.

```
python3     # MacOS/Linux
python      # Windows
```
```python
from save_thread_result import ThreadWithResult

# As of Release 0.0.3, you can also specify values for
#`group`, `name`, and `daemon` if you want to set those
# values manually.
thread = ThreadWithResult(
    target = my_function,
    args   = (my_function_arg1, my_function_arg2, ...)
    kwargs = (my_function_kwarg1=kwarg1_value, my_function_kwarg2=kwarg2_value, ...)
)

thread.start()
thread.join()
if getattr(thread, 'result', None):
    print(thread.result)
else:
    # thread.result attribute not set - something caused
    # the thread to terminate BEFORE the thread finished
    # executing the function passed in through the
    # `target` argument
    print('ERROR! Something went wrong while executing this thread, and the function you passed in did NOT complete!!')
```
To see why checking `getattr(thread, 'result', None)` might be necessary for a more complicated scenario, [see this modification in a testing module](https://github.com/Shail-Shouryya/yt_videos_list/commit/27cc6a9fde087715c7179d6745b139daf3bb731e) from the [`yt_videos_list` package](https://github.com/Shail-Shouryya/yt_videos_list/tree/master/python).

Verified scenario:
  - see this commit: [Import ThreadWithResult from save_thread_result package (↑ DRY)](https://github.com/Shail-Shouryya/yt_videos_list/commit/164434d6188efb2971979e4ba35b01e6615aece2)
</details>

<details>
  <summary><b>Seeing <b>all</b> available methods and attributes for <code>ThreadWithResult</code> class</b></summary>

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
  <a href="https://pypistats.org/packages/save-thread-result"><img alt="PyPI - Daily Downloads" src="https://img.shields.io/pypi/dd/save-thread-result?labelColor=black&color=blue&label=PyPI%20downloads%20%28excludes%20mirrors%29" width="275"></a>
  <a href="https://pypistats.org/packages/save-thread-result"><img alt="PyPI - Weekly Downloads" src="https://img.shields.io/pypi/dw/save-thread-result?labelColor=black&color=yellow&label=PyPI%20downloads%20%28excludes%20mirrors%29"width="275"></a>
  <a href="https://pypistats.org/packages/save-thread-result"><img alt="PyPI - Monthly Downloads" src="https://img.shields.io/pypi/dm/save-thread-result?labelColor=black&color=blue&label=PyPI%20downloads%20%28excludes%20mirrors%29"width="275"></a>
  <br>
  <a href="https://pepy.tech/project/save-thread-result"><img alt="PePY Weekly Downloads" src="https://static.pepy.tech/personalized-badge/save-thread-result?period=week&units=international_system&left_color=black&right_color=yellow&left_text=PePY%20Downloads/week%20%28includes%20mirrors%29" width="275"></a>
  <a href="https://pepy.tech/project/save-thread-result"><img alt="PePY Monthly Downloads" src="https://static.pepy.tech/personalized-badge/save-thread-result?period=month&units=international_system&left_color=black&right_color=blue&left_text=PePY%20Downloads/month%20%28includes%20mirrors%29" width="275"></a>
  <a href="https://pepy.tech/project/save-thread-result"><img alt="PePY Total Downloads" src="https://static.pepy.tech/personalized-badge/save-thread-result?period=total&units=international_system&left_color=black&right_color=yellow&left_text=PePY%20Downloads%20Total%20%28includes%20mirrors%29" width="275"></a>
</p>

If you found this interesting or useful, **please consider starring this repo** at [GitHub](https://github.com/Shail-Shouryya/save-thread-result) so other people can more easily find and use this. Thanks!
