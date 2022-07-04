# Python API

<details>
  <summary><b>Installing the module</b></summary>

Enter the following in your command line:

```python
# if something isn't working properly, try rerunning this
# the problem may have been fixed with a newer version

pip3 install -U save-thread-result     # MacOS/Linux
pip  install -U save-thread-result     # Windows

# if that doesn't work:

python3 -m pip install -U save-thread-result     # MacOS/Linux
python  -m pip install -U save-thread-result     # Windows
```
</details>

<details>
  <summary><b>Initializing and using the <code>ThreadWithResult</code> class</b></summary>

This module uses a [`threading.Thread`](https://docs.python.org/3/library/threading.html#threading.Thread) subclass `ThreadWithResult` that saves the result of a thread (from [`threading`](https://docs.python.org/3/library/threading.html) built-in module in the [Python Standard library](https://docs.python.org/3/library/index.html)) as its `result` attribute - i.e. after the thread finishes running, call `thread.result` to get the return value from the function that ran on that thread.

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
    kwargs = {my_function_kwarg1: kwarg1_value, my_function_kwarg2: kwarg2_value, ...}
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
To see why checking `getattr(thread, 'result', None)` might be necessary for a more complicated scenario, [see this modification in a testing module](../../../../yt-videos-list/commit/27cc6a9fde087715c7179d6745b139daf3bb731e) from the [`yt-videos-list` package](../../../../yt-videos-list/tree/main/python). NOTE that the `result` attribute was named `failed` in this commit (the subclass implementation here assigned the result of the threaded function to `self.failed` instead of to `self.result`)!

Verified scenario:
  - see this commit: [Import ThreadWithResult from save_thread_result package (↑ DRY)](../../../../yt-videos-list/commit/164434d6188efb2971979e4ba35b01e6615aece2)
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

# OR

import save_thread_result
help(save_thread_result.ThreadWithResult)

# SEEING MODULE METADATA
import save_thread_result
help(save_thread_result)
```

</details>

<details>
  <summary><b>Motivation for creating this module</b></summary>

I created this module because I needed to [store the result](../../../../yt-videos-list/commit/8fc62703047b9f8de287306239885cd5138a8d7e) of a thread [while running tests](../../../../yt-videos-list/blob/main/python/tests/test_shared.py) for the `yt-videos-list` module and there seemed to be no simple way to get the result from `threading.Thread()` without importing other modules, creating a `Queue`, or creating a `list` and then storing the result in the list, or doing other hacky things.
  <details>
    <summary><b>Sources I looked at before creating the custom class below</b></summary>

  - [Return value from thread](https://stackoverflow.com/questions/1886090/return-value-from-thread)
  - [Threading in python: retrieve return value when using target= [duplicate]](https://stackoverflow.com/questions/2577233/threading-in-python-retrieve-return-value-when-using-target)
  - [How to get the return value from a thread in python?](https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python)
  - [Using Python Threading and Returning Multiple Results (Tutorial)](https://www.shanelynn.ie/using-python-threading-for-multiple-results-queue/)
  - [How to get the return value from a thread using python](https://www.edureka.co/community/31966/how-to-get-the-return-value-from-a-thread-using-python)
  - [How to manage python threads results?](https://stackoverflow.com/questions/3239617/how-to-manage-python-threads-results#3239815)
  - [How to obtain the results from a pool of threads in python?](https://stackoverflow.com/questions/26104512/how-to-obtain-the-results-from-a-pool-of-threads-in-python)
  - [Google search](https://www.google.com/search?hl=en&q=python%20save%20thread%20result)
  </details>

  <details>
    <summary><b>Implementation in <code>yt-videos-list</code></b></summary>

  - see commits:
    - [Add custom class to store thread result](../../../../yt-videos-list/commit/8fc62703047b9f8de287306239885cd5138a8d7e)
    - [Make ThreadWithResult attribute names more descriptive](../../../../yt-videos-list/commit/f1d58f6deeb2becf9038a94c3fb964bccc5321d3)
    - [Add ThreadWithResult class docstring (test_shared.py)](../../../../yt-videos-list/commit/b10480b6979f96443ab9e2e62e515c4da30eccdb)
    - [Import ThreadWithResult from `save_thread_result` package (↑ DRY)](../../../../yt-videos-list/commit/164434d6188efb2971979e4ba35b01e6615aece2)
  - see `yt-videos-list` [Release 0.5.0](../../../../yt-videos-list/releases/tag/v0.5.0) for other threading bugs and workarounds!
  </details>
</details>

<details>
  <summary><b><code>ThreadWithResult</code> logic</b></summary>

This module is really only 6 lines of code:
```python
import threading

class ThreadWithResult(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None):
        def function():
            self.result = target(*args, **kwargs)
        super().__init__(group=group, target=function, name=name, daemon=daemon)
```

For a more detailed explanation, read through the [docstrings](./save_thread_result/__init__.py) in the `thread_with_result` module. This is also accessible through the python interpreter with
```
python3     # MacOS/Linux
python      # Windows
```
```python
import save_thread_result
help(save_thread_result)
```
</details>
