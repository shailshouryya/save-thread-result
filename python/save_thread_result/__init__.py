'''
Simple subclass wrapper around `threading.Thread` to get the return value
from a thread in python (from `threading` built-in module in Python Standard library).
Exact same interface for creating an instance of this threading sublcass as `threading.Thread`!
'''
from .thread_with_result import ThreadWithResult


__version__              = '0.0.5'
__author__               = 'Shail-Shouryya'
__email__                = 'shailshouryya@gmail.com'
__development_status__   = '4 - Beta'
__intended_audience__    = 'Developers'
__license__              = 'OSI Approved :: Apache License 2.0'
__ideal_python_version__ = 'Python 3.0+'
__source__               = 'https://github.com/Shail-Shouryya/save-thread-result'
