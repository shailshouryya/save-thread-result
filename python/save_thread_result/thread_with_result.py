'''
Contains `threading.Thread` subclass that saves the result of a thread
as its `result` attribute - i.e. call `thread_with_result_instance_1.result`
after `thread_with_result_instance_1` finishes running to get the return
value from the function that ran on that thread.
'''
import threading

class ThreadWithResult(threading.Thread):
    '''
    Helper class used solely for saving the result of a function called
    through the threading interface, since `some_thread_object.start()`
    executes and returns immediately, without waiting for the thread
    to finish. The name of the function to run on a separate thread
    should be passed in through the `target` argument, and any
    arguments for the function should be passed in through the
    `args` argument.

    EXPLANATION:

    We create a closure function that runs the actual function we want
    to run on a separate thread and enclose the function passed to
    `target` inside the closure function, and pass the CLOSURE FUNCTION
    as the function to the `target` argument for `threading.Thread`.

    Since the function we want to run on a separate thread is no longer
    the function passed directly to `threading.Thread` (remember
    we pass the closure function instead!), we save the result of
    the enclosed function as the `self.failed` attribute for the
    actual instance of this class.

    We use inheritance to initialize this instance with the
    closure function as the `target` function and no arguments
    for `args` since we pass the arguments to our actual function
    inside the closure function.
    '''
    def __init__(self, target, args):
        self.function_to_thread = target
        self.function_arguments = args
        def function():
            self.result = self.function_to_thread(*self.function_arguments)
        super().__init__(target=function, args=())
