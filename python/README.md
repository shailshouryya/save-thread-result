# Python API

## Quickstart

Installing the `save_thread_result` module:
```
pip3 install -U save-thread-result     # MacOS/Linux
pip  install -U save-thread-result     # Windows

# if that doesn't work:
python3 -m pip install -U save-thread-result     # MacOS/Linux
python  -m pip install -U save-thread-result     # Windows
```

Using the `ThreadWithResult` class from the `save_thread_result` module:
```
from save_thread_result import ThreadWithResult


# As of Release 0.0.3, you can also specify values for
# `group`, `name`, and `daemon` if you want to set those
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

Reading the documentation for more information:
```
from save_thread_result import ThreadWithResult
help(ThreadWithResult)
```

## Short explanation

This module uses a [`threading.Thread`](https://docs.python.org/3/library/threading.html#threading.Thread) subclass `ThreadWithResult` that saves the result of a thread (from [`threading`](https://docs.python.org/3/library/threading.html) built-in module in the [Python Standard library](https://docs.python.org/3/library/index.html)) as its `result` attribute - i.e. after the thread finishes running, call `thread.result` to get the return value from the function that ran on that thread.

## Examples

Dummy example:
```
from save_thread_result import ThreadWithResult

import time, random


def function_to_thread(n):
    count = 0
    while count < 3:
            print(f'Still running thread {n}...')
            count +=1
            time.sleep(3)
    result = random.random()
    print(f'Return value of thread {n} should be: {result}')
    return result


def main():
    thread1 = ThreadWithResult(target=function_to_thread, args=(1,))
    thread2 = ThreadWithResult(target=function_to_thread, args=(2,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
    print(thread1.result)
    print(thread2.result)

main()
```

<details>
  <summary><b>More information</b></summary>

  <details>
    <summary><b>Sources I looked at before creating the custom class</b></summary>

  - [Return value from thread](https://stackoverflow.com/questions/1886090/return-value-from-thread)
  - [Threading in python: retrieve return value when using target= [duplicate]](https://stackoverflow.com/questions/2577233/threading-in-python-retrieve-return-value-when-using-target)
  - [How to get the return value from a thread in python?](https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python)
  - [Using Python Threading and Returning Multiple Results (Tutorial)](https://www.shanelynn.ie/using-python-threading-for-multiple-results-queue/)
  - [How to get the return value from a thread using python](https://www.edureka.co/community/31966/how-to-get-the-return-value-from-a-thread-using-python)
  - [How to manage python threads results?](https://stackoverflow.com/questions/3239617/how-to-manage-python-threads-results#3239815)
  - [How to obtain the results from a pool of threads in python?](https://stackoverflow.com/questions/26104512/how-to-obtain-the-results-from-a-pool-of-threads-in-python)
  - [Google search](https://www.google.com/search?hl=en&q=python%20save%20thread%20result)
  </details>
</details>
