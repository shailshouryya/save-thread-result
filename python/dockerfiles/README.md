# Overview

This directory contains `Dockerfile`s for using the `save_thread_result` package on different versions of python.

NOTE! The `COPY` command (in the Dockerfile in this directory) will only work properly if the command using the Dockerfile to build the Docker image is called from the `save-thread-result/python` directory and will NOT work if called from the `save-thread-result/python/tests` directory or the `save-thread-result` directory
