'''
Simple subclass wrapper around `threading.Thread` to get the return value
from a thread in python (from `threading` built-in module in Python Standard library).
Exact same interface for creating an instance of this threading sublcass as `threading.Thread`!
'''
import time
import threading
from datetime import datetime


__version__              = '0.0.6'
__author__               = 'Shail-Shouryya'
__email__                = 'shailshouryya@gmail.com'
__development_status__   = '4 - Beta'
__intended_audience__    = 'Developers'
__license__              = 'OSI Approved :: Apache License 2.0'
__ideal_python_version__ = 'Python 3.0+'
__source__               = 'https://github.com/Shail-Shouryya/save-thread-result'


class ThreadWithResult(threading.Thread):
    '''
    The `threading.Thread` subclass ThreadWithResult saves the result of a thread
    as its `result` attribute - i.e. call `thread_with_result_instance_1.result`
    after `thread_with_result_instance_1` finishes running to get the return
    value from the function that ran on that thread.

    thread = ThreadWithResult(
        target = my_function,
        args   = (my_function_arg1, my_function_arg2, ...)
        kwargs = {my_function_kwarg1: kwarg1_value, my_function_kwarg2: kwarg2_value, ...}
    )

    thread.start()

    thread.join()

    thread.result # returns value returned from function passed in to the `target` argument!


    NOTE: As of Release 0.0.3, you can also specify values for
    the `group`, `name`, and `daemon` arguments if you want to
    set those values manually.

    For details about the interface features available from `threading.Thread`,
    see documentation under "Method resolution order" - accessible
    from the python interpreter with:
    help(ThreadWithResult)

    OVERVIEW:

    ThreadWithResult is a `threading.Thread` subclass used to save the
    result of a function called through the threading interface, since

    thread = threading.Thread(
        target = my_function,
        args   = (my_function_arg1, my_function_arg2, ...)
        kwargs = {my_function_kwarg1: kwarg1_value, my_function_kwarg2: kwarg2_value, ...}
    )

    thread.start()

    thread.join()

    thread.result # does not work!


    executes and returns immediately, without waiting for the thread
    to finish AND WITHOUT providing any way to get the return result
    of the function that ran on the thread.

    The name of the function to run on a separate thread should
    be passed to `ThreadWithResult` through the `target` argument,
    and any arguments for the function should be passed in
    through the `args` and `kwargs` arguments.

    You can also specify `threading.Thread` attributes such as
    `group`, `name`, and `daemon` by passing in the value you want to
    set them to as keyword arguments to `ThreadWithResult`

    EXPLANATION:

    We create a closure function that runs the actual function we want
    to run on a separate thread and enclose the function passed to
    `target` inside the closure function, and pass the CLOSURE FUNCTION
    as the function to the `target` argument for `threading.Thread`.

    Since the function we want to run on a separate thread is no longer
    the function passed directly to `threading.Thread` (remember
    we pass the closure function instead!), we save the result of
    the enclosed function to the `self.result` attribute of the
    instance.

    We use inheritance to initialize this instance with the
    closure function as the `target` function and no arguments
    for `args` or `kwargs` since
    we pass the arguments to our actual function
    inside the closure function.

    All other attributes (`group`, `name`, and `daemon`)
    are initialized in the parent `threading.Thread` class
    during the `super()` call.



    NOTE that with release 0.0.7, you can also specify if
    you want the ThreadWithResult instance to print when the
    thread starts, ends, and how long the thread took to execute!

    If you want to mute this for all ThreadWithResult instances,
    set the class `log_thread_status` variable to False:

    ThreadWithResult.log_thread_status = False


    If you only want to mute this for specific instances of
    ThreadWithResult, set the `log_thread_status` attribute for the
    specific instance to False:

    thread_with_result_instance.log_thread_status = False



    ========================================================
    | If you found this interesting or useful,             |
    | ** please consider starring this repo at **          |
    | https://github.com/Shail-Shouryya/save-thread-result |
    | so other people can                                  |
    | more easily find and use this. Thanks!               |
    ========================================================
    '''
    log_thread_status = True
    log_files         = None

    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None):
        def function():
            if self.log_thread_status is True:
                start       = time.time()
                thread_name = f'[{threading.current_thread().name}]'
                utc_offset  = time.strftime('%z')
                now         = lambda: datetime.now().isoformat() + utc_offset
                message     = f'{now()} {thread_name:>12} Starting thread...\n'
                print(message)
                if self.log_files is not None:
                    try:
                        for file in self.log_files:
                            try:
                                file.write(message)
                            except AttributeError as error_message:
                                # AttributeError: 'str' object has no attribute 'write'
                                print(f'ERROR! Could not write to {file}. Please make sure that every object in {self.log_files} supports the .write() method. The exact error was:\n{error_message}')
                    except TypeError as error_message:
                        # TypeError: 'int' object is not iterable
                        print(f'ERROR! Could not write to {self.log_files}. Please make sure that the log_files attribute for {self.__class__.name} is an iterable object containing objects that support the .write() method. The exact error was:\n{error_message}')
            self.result = target(*args, **kwargs)
            if self.log_thread_status is True:
                end     = time.time()
                message = f'{now()} {thread_name:>12} Finished thread! This thread took {end - start} seconds to complete.\n'
                print(message)
                if self.log_files is not None:
                    try:
                        for file in self.log_files:
                            try:
                                file.write(message)
                            except AttributeError as error_message:
                                # AttributeError: 'str' object has no attribute 'write'
                                print(f'ERROR! Could not write to {file}. Please make sure that every object in {self.log_files} supports the .write() method. The exact error was:\n{error_message}')
                    except TypeError as error_message:
                        # TypeError: 'int' object is not iterable
                        print(f'ERROR! Could not write to {self.log_files}. Please make sure that the log_files attribute for {self.__class__.name} is an iterable object containing objects that support the .write() method. The exact error was:\n{error_message}')

        super().__init__(group=group, target=function, name=name, daemon=daemon)
