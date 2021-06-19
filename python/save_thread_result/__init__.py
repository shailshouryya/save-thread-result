'''
Simple subclass wrapper around `threading.Thread` to get the return value
from a thread in python. Exact same interface as `threading.Thread`!
🌟 Star this repo if you found this useful! 🌟
https://github.com/Shail-Shouryya/save-thread-result
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


    executes and returns immediately after the thread finishes,
    WITHOUT providing any way to get the returned result
    of the function that ran on the thread.


    USAGE:

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
    as the function to the `target` argument to `threading.Thread`.

    Since the function we want to run on a separate thread is no longer
    the function passed directly to `threading.Thread` (remember,
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
    you want the ThreadWithResult instance to log when the
    thread starts, ends, and how long the thread takes to execute!

    If you want to mute logging this message to the terminal for all
    ThreadWithResult instances, set the
    `log_thread_status` class attribute to False:

    ThreadWithResult.log_thread_status = False


    If you only want to mute logging this message to the terminal for
    a specific instance of ThreadWithResult, set the
    `log_thread_status` attribute for the specific instance to False:

    thread_with_result_instance.log_thread_status = False

    Keep in mind python prioritizes the `log_thread_status` instance attribute
    over the `log_thread_status` class attribute!


    If you want to log this message to an output file (or multiple output files)
    for all ThreadWithResult instances, set the
    `log_files` class attribute to an iterable object contatining
    objects that support the .write() method:

    ThreadWithResult.log_files = [file_object_1, file_object_2]


    If you only want to log this message to an output file (or multiple output files)
    for a specific instance of ThreadWithResult, set the
    `log_files` attribute for the specific instance to an iterable
    object contatining objects that support the .write() method:

    thread_with_result_instance.log_files = [file_object_1, file_object_2]

    Keep in mind python prioritizes the `log_files` instance attribute
    over the `log_files` class attribute!

    NOTE: since python prioritizes instance attributes over class attributes,
    if both the instance attribute and class attribute are set to different values,
    python uses the value set for the instance attribute.
    For more information, look up:
    class attributes vs instance attributes in python
    scope resolution using the LEGB rule for python

    Also note, by default the `log_thread_status`
    class attribute is set to `True`, and the `log_files`
    class attribute set to `None` - neither attributes
    exist as instance attributes by default!


    For an example that uses this logging feature in a real application, see how
    the `create_list_from()` method of the ListCreator class uses ThreadWithResult
    at https://github.com/Shail-Shouryya/yt-videos-list/blob/main/python/dev/__init__.py


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
            log_condition = self.log_thread_status is True or self.log_files is not None
            if log_condition:
                start       = time.time()
                thread_name = '[' + threading.current_thread().name + ']'
                utc_offset  = time.strftime('%z')
                now         = lambda: datetime.now().isoformat() + utc_offset + ' '
                message     = now() + thread_name.rjust(12) + ' Starting thread...'
                self.__log(message)
            self.result = target(*args, **kwargs)
            if log_condition:
                end     = time.time()
                message = now() + thread_name.rjust(12) + ' Finished thread! This thread took ' + str(end - start) + ' seconds to complete.'
                self.__log(message)
        super().__init__(group=group, target=function, name=name, daemon=daemon)

    def __log(self, message):
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
        if self.log_files is not None:
            try:
                for file in self.log_files:
                    try:
                        file.write(message + '\n')
                    except AttributeError as error_message:
                        # example exception:
                        # AttributeError: 'str' object has no attribute 'write'
                        print('ERROR! Could not write to ' + str(file) + '. Please make sure that every object in ' + str(self.log_files) + ' supports the .write() method. The exact error was:\n' + str(error_message))
            except TypeError as error_message:
                # example exception:
                # TypeError: 'int' object is not iterable
                print('ERROR! Could not write to ' + str(self.log_files) + '. Please make sure that the log_files attribute for ' + str(self.__class__.name) + ' is an iterable object containing objects that support the .write() method. The exact error was:\n' + str(error_message))
        if self.log_thread_status is True:
            print(message)
