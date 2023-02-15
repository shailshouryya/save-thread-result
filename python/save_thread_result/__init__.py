'''
Simple subclass wrapper around `threading.Thread` to get the return value
from a thread in python. Exact same interface as `threading.Thread`!

'''
import sys
import time
import threading
from datetime import datetime


__version__              = '0.1.0'


class ThreadWithResult(threading.Thread):
    '''
    The `threading.Thread` subclass `ThreadWithResult` saves the result of a thread
    as its `result` attribute - i.e. call `thread_with_result_instance_1.result`
    after `thread_with_result_instance_1` finishes running to get the return
    value from the function that ran on that thread:

    >>> thread = ThreadWithResult(
        target = my_function,
        args   = (my_function_arg1, my_function_arg2, ...)
        kwargs = {my_function_kwarg1: kwarg1_value, my_function_kwarg2: kwarg2_value, ...}
    )
    >>> thread.start()
    >>> thread.join()
    >>> thread.result # returns value returned from function passed in to the `target` argument!




    NOTE: As of Release 0.0.3, you can also specify values for
    the `group`, `name`, and `daemon` arguments if you want to
    set those values manually.

    For details about the interface features available from `threading.Thread`,
    see documentation under "Method resolution order" - accessible
    from the python interpreter with:
    help(ThreadWithResult)




    OVERVIEW:
    `ThreadWithResult` is a `threading.Thread` subclass used to save the
    result of a function called through the threading interface, since

    >>> thread = threading.Thread(
        target = my_function,
        args   = (my_function_arg1, my_function_arg2, ...)
        kwargs = {my_function_kwarg1: kwarg1_value, my_function_kwarg2: kwarg2_value, ...}
    )
    >>> thread.start()
    >>> thread.join()
    >>> thread.result # does not work!

    executes and returns immediately after the thread finishes,
    WITHOUT providing any way to get the return value
    from the function that ran on that thread.




    USAGE:
    The name of the function to run on a separate thread should
    be passed to `ThreadWithResult` through the `target` argument,
    and any arguments for the function should be passed in
    through the `args` and `kwargs` arguments.

    You can also specify `threading.Thread` attributes such as
    `group`, `name`, and `daemon` by passing in the value you want to
    set them to as keyword arguments to `ThreadWithResult`




    EXPLANATION:
    We create a closure function to run the actual function we want
    to run on a separate thread, enclose the function passed to
    `target` - along with the arguments provided to `args` and `kwargs` -
    inside the closure function, and pass the CLOSURE FUNCTION
    as the function to the `target` argument in the
    `super.__init__()` call to `threading.Thread`:
    super().__init__(group=group, target=closure_function, name=name, daemon=daemon)

    Since the function we want to run on a separate thread is no longer
    the function passed directly to `threading.Thread` (remember,
    we pass the closure function instead!), we save the result of
    the enclosed function to the `self.result` attribute of the
    instance.

    We use inheritance to initialize this instance with the
    closure function as the `target` function and no arguments
    for `args` or `kwargs` (since we pass
    the `args` and `kwargs` arguments to the original
    `target` function INSIDE the closure function).

    All other attributes (`group`, `name`, and `daemon`)
    are initialized in the parent `threading.Thread` class
    during the `super().__init__()` call.




    NOTE that with release 0.0.7, you can also specify if
    you want the `ThreadWithResult` instance to log when the
    thread starts, ends, and how long the thread takes to execute!


    If you want to mute logging this message to the terminal for all
    `ThreadWithResult` instances, set the
    `log_thread_status` class attribute to False:

    >>> ThreadWithResult.log_thread_status = False


    If you only want to mute logging this message to the terminal for
    a specific instance of `ThreadWithResult`, set the
    `log_thread_status` attribute for the specific instance to False:

    >>> thread_with_result_instance.log_thread_status = False

    ------------------------------------------------------------------------------
    | Keep in mind python prioritizes the `log_thread_status` instance attribute |
    | over the `log_thread_status` class attribute!                              |
    ------------------------------------------------------------------------------



    If you want to log this message to an output file (or multiple output files)
    for all `ThreadWithResult` instances, set the
    `log_files` class attribute to an iterable object contatining
    objects that support the .write() method:

    >>> ThreadWithResult.log_files = [file_object_1, file_object_2]


    If you only want to log this message to an output file (or multiple output files)
    for a specific instance of `ThreadWithResult`, set the
    `log_files` attribute for the specific instance to an iterable
    object contatining objects that support the .write() method:

    >>> thread_with_result_instance.log_files = [file_object_1, file_object_2]

    ----------------------------------------------------------------------
    | Keep in mind python prioritizes the `log_files` instance attribute |
    | over the `log_files` class attribute!                              |
    ----------------------------------------------------------------------



    NOTE: since python prioritizes instance attributes over class attributes,
    if both the instance attribute and class attribute are set to different values,
    python uses the value set for the instance attribute.
    For more information, look up:
      - class attributes vs instance attributes in python
      - scope resolution using the LEGB rule for python

    Also note, by default the `log_thread_status`
    class attribute is set to `True`, and the `log_files`
    class attribute set to `None` - neither attributes
    exist as instance attributes by default!
    '''
    log_thread_status = True
    log_files         = None

    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None):
        def closure_function():
            log_condition = self.log_thread_status is True or self.log_files is not None
            if log_condition:
                time_start         = time.time()
                perf_counter_start = _time_perf_counter()
                thread_name        = '[' + threading.current_thread().name + ']'
                utc_offset         = time.strftime('%z')
                now                = lambda: datetime.now().isoformat() + utc_offset + ' '
                message            = now() + thread_name.rjust(12) + ' Starting thread...'
                _log(self, message)
            self.result = target(*args, **kwargs)
            if log_condition:
                time_end         = time.time()
                perf_counter_end = _time_perf_counter()
                formatted_perf   = _format_perf_counter_info(perf_counter_start, perf_counter_end)
                message          = now() + thread_name.rjust(12) + ' Finished thread! This thread took ' + str(time_end - time_start) + ' time.time() seconds' + formatted_perf + ' to complete.'
                _log(self, message)
        if sys.version_info.major == 3 and sys.version_info.minor >= 10:
            # commit 98c16c991d6e70a48f4280a7cd464d807bdd9f2b in the cpython repository starts adding
            # the function name of the `target` argument to the thread name:
            #     *name* is the thread name. By default, a unique name is constructed
            #     of the form "Thread-*N*" where *N* is a small decimal number,
            #     or "Thread-*N* (target)" where "target" is ``target.__name__`` if the
            #     *target* argument is specified BUT the *name* argument is omitted.
            # HOWEVER, since we pass the
            # original `target` argument to the `closure_function` here and then pass `closure_function`
            # as the new `target` argument in the `super()` call, the thread name (as seen by the base
            # `threading.Thread` class) will ALWAYS be "closure_function" regardless of what function
            # is running inside `closure_function` - to make the name more helpful, we manually overwrite
            # the `closure_function.__name__` attribute here to include the original `target` function's name
            #   - see the following for more information:
            #     - https://github.com/python/cpython/issues/85999
            #     - https://github.com/python/cpython/issues/59705
            #     - https://github.com/python/cpython/issues/85905
            #     - https://github.com/python/cpython/pull/22357
            #     - https://github.com/python/cpython/issues/85999
            #     - https://bugs.python.org/issue41833
            if name is None and target is not None:
                closure_function.__name__ = self.__class__.__name__ + '.' + 'closure_function' + '(' + str(target.__name__) + ')'
        super().__init__(group=group, target=closure_function, name=name, daemon=daemon)

def _log(thread_with_result_instance, message):
    '''
    Helper function to print when the thread
    starts, ends, and how long the thread takes to execute.

    This function runs and prints the thread information to the
    terminal when any of the following statements are true:
        * the instance attribute `log_thread_status` is `True`
        * the instance attribute `log_thread_status` is unset but
            the class attribute `log_thread_status` is `True`
        * the instance attribute `log_files` is
        an iterable object containing objects that support the .write() method
        * the instance attribute `log_files` is unset but
            the class attribute is an iterable object containing objects that support the .write() method

    This function also logs the information to every location in
    `log_files` in addition to printing the thread information
    to the terminal if the instance or class attribute `log_files` is an
    iterable object containing objects that support the .write() method.
    '''
    if thread_with_result_instance.log_files is not None:
        try:
            for file in thread_with_result_instance.log_files:
                try:
                    file.write(message + '\n')
                except AttributeError as error_message:
                    # example exception:
                    # AttributeError: 'str' object has no attribute 'write'
                    print('ERROR! Could not write to ' + str(file) + '. Please make sure that every object in ' + str(thread_with_result_instance.log_files) + ' supports the .write() method. The exact error was:\n' + str(error_message))
        except TypeError as error_message:
            # example exception:
            # TypeError: 'int' object is not iterable
            print('ERROR! Could not write to ' + str(thread_with_result_instance.log_files) + '. Please make sure that the log_files attribute for ' + str(thread_with_result_instance.__class__.name) + ' is an iterable object containing objects that support the .write() method. The exact error was:\n' + str(error_message))
    if thread_with_result_instance.log_thread_status is True:
        print(message)


# use helper functions for time.perf_counter() since function became available only after python release 3.3
def _time_perf_counter():
    if sys.version_info.major == 3 and sys.version_info.minor >= 3:
        return time.perf_counter()
    return None

def _format_perf_counter_info(perf_counter_start, perf_counter_end):
    if sys.version_info.major == 3 and sys.version_info.minor >= 3:
        return ' (' + str(perf_counter_end - perf_counter_start) + ' time.perf_counter() seconds)'
    return ''
