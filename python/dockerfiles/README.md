# Overview

This directory contains `Dockerfile`s for using the `save_thread_result` package on different versions of python.

## Building the `Docker` image

NOTE! The `COPY` command (in the Dockerfile in this directory) will only work properly if the command using the Dockerfile to build the Docker image is called from the `save-thread-result/python` directory and will NOT work if called from the `save-thread-result/python/tests` directory or the `save-thread-result` directory

### Command to build the `Docker` image

```
docker build --tag save_thread_result-debian-bullseye-slim-python3_0-from_source --file ./dockerfiles/debian-bullseye-slim-python3_0-from_source .
docker build --tag save_thread_result-debian-bullseye-slim-python3_1-from_source --file ./dockerfiles/debian-bullseye-slim-python3_1-from_source .
docker build --tag save_thread_result-debian-bullseye-slim-python3_2-from_source --file ./dockerfiles/debian-bullseye-slim-python3_2-from_source .
docker build --tag save_thread_result-debian-bullseye-slim-python3_3-from_source --file ./dockerfiles/debian-bullseye-slim-python3_3-from_source .
docker build --tag save_thread_result-debian-bullseye-slim-python3_4-from_source --file ./dockerfiles/debian-bullseye-slim-python3_4-from_source .
docker build --tag save_thread_result-debian-bullseye-slim-python3_5-from_source --file ./dockerfiles/debian-bullseye-slim-python3_5-from_source .
docker build --tag save_thread_result-debian-bullseye-slim-python3_6-from_source --file ./dockerfiles/debian-bullseye-slim-python3_6-from_source .
docker build --tag save_thread_result-debian-bullseye-slim-python3_7-from_source --file ./dockerfiles/debian-bullseye-slim-python3_7-from_source .
docker build --tag save_thread_result-debian-bullseye-slim-python3_8-from_source --file ./dockerfiles/debian-bullseye-slim-python3_8-from_source .
docker build --tag save_thread_result-debian-bullseye-slim-python3_9-from_source --file ./dockerfiles/debian-bullseye-slim-python3_9-from_source .
docker build --tag save_thread_result-debian-bullseye-slim-python3_10-from_source --file ./dockerfiles/debian-bullseye-slim-python3_10-from_source .
docker build --tag save_thread_result-debian-bullseye-slim-python3_11-from_source --file ./dockerfiles/debian-bullseye-slim-python3_11-from_source .
docker build --tag save_thread_result-debian-bullseye-slim-python3_12-from_source --file ./dockerfiles/debian-bullseye-slim-python3_12-from_source .
```


### Using `clang` instead of `gcc` for `python3.2` and `python3.3`

Attempting to build `Python-3.2.6` (and other patch releases for `Python-3.2`) and `Python3.3.7` (and other patch releases for `Python-3.3`) from source fails on the `debian:bullseye-20231120-slim` base image due to a `Segmentation fault` (see the [stack trace for Docker image build failure](#stack-trace-for-docker-image-build-failure) section below). This seemed odd, but attempting to rebuild the Dockerfile with no changes consistently resulted in the same error.

Searching for potential fixes led to many tangential issues people ran into in the past, but [this Stack Overflow answer](https://stackoverflow.com/a/73267352) linked to [stsewd's comment on a `pyenv` issue thread](https://github.com/pyenv/pyenv/issues/1889#issuecomment-833587851) which provided the simple solution of switching the compiler used to build Python to `clang`. (The Dockerfiles here used `gcc`, but I'm not sure which specific compiler stsewd or anyone else in that thread was using.) This issue was filed for `Fedora 34`, but this was(/is) likely an OS agnostic issue, since this affected the source build on `Debian 11` as well. [ni-balexand mentioned (2021-05-10)](https://github.com/pyenv/pyenv/issues/1889#issuecomment-837697366) incorrect object allocation code caused this problem (which was fixed in https://bugs.python.org/file44413/alignment.patch):

```
diff -r 388d58a5de9e Include/objimpl.h
--- a/Include/objimpl.h	Tue Sep 06 15:58:40 2016 -0700
+++ b/Include/objimpl.h	Tue Sep 06 17:11:43 2016 -0700
@@ -250,7 +250,7 @@
         union _gc_head *gc_prev;
         Py_ssize_t gc_refs;
     } gc;
-    double dummy;  /* force worst-case alignment */
+    long double dummy;  /* force worst-case alignment */
 } PyGC_Head;

 extern PyGC_Head *_PyGC_generation0;
diff -r 388d58a5de9e Objects/obmalloc.c
--- a/Objects/obmalloc.c	Tue Sep 06 15:58:40 2016 -0700
+++ b/Objects/obmalloc.c	Tue Sep 06 17:11:43 2016 -0700
@@ -643,8 +643,8 @@
  *
  * You shouldn't change this unless you know what you are doing.
  */
-#define ALIGNMENT               8               /* must be 2^N */
-#define ALIGNMENT_SHIFT         3
+#define ALIGNMENT               16               /* must be 2^N */
+#define ALIGNMENT_SHIFT         4

 /* Return the number of bytes in size class I, as a uint. */
 #define INDEX2SIZE(I) (((uint)(I) + 1) << ALIGNMENT_SHIFT)
```

Gilles Bardoux mentioned a fix that is the direct opposite (changing `long double dummy` to `double dummy` instead of changing `double dummy` to `long double dummy` in `Include/objimpl.h`) earlier (2019-10-21) at https://bugs.python.org/issue37930 compared to the patch ni-balexand mentioned:

```
--- a/Include/objimpl.h
+++ b/Include/objimpl.h
@@ -248,7 +248,7 @@ typedef union _gc_head {
         union _gc_head *gc_prev;
         Py_ssize_t gc_refs;
     } gc;
-    long double dummy;  /* force worst-case alignment */
+    double dummy;  /* force worst-case alignment */
 } PyGC_Head;

 extern PyGC_Head *_PyGC_generation0;
```

<strike>In either case, it appears that the `gcc` compiler is more picky/less flexible or has a different implementation of `long double` and `double` compared to the `clang` compiler.</strike>

The `Include/objimpl.h` definition in both the `Python-3.2.6` and `Python3.3.7` contains

```
/* GC information is stored BEFORE the object structure. */
#ifndef Py_LIMITED_API
typedef union _gc_head {
    struct {
        union _gc_head *gc_next;
        union _gc_head *gc_prev;
        Py_ssize_t gc_refs;
    } gc;
    long double dummy;  /* force worst-case alignment */
} PyGC_Head;
```

and manually changing the `long double dummy` to `double dummy` allows `gcc` to compile without the

```
Segmentation fault
make: *** [Makefile:467: sharedmods] Error 139
```

Therefore, it appears the fix Gilles Bardoux suggested is the actual fix.

Directly related links:
- https://bugs.python.org/issue37930
- https://stackoverflow.com/a/73267352
- https://github.com/pyenv/pyenv/issues/1889#issuecomment-833587851


Links discussing `Error 139`/`Segmentation fault` issues:
- https://stackoverflow.com/questions/49414841/process-finished-with-exit-code-139-interrupted-by-signal-11-sigsegv
- https://stackoverflow.com/questions/63399665/how-can-i-solve-process-finished-with-exit-code-139-interrupted-by-signal-11
- https://stackoverflow.com/questions/41200364/why-am-i-getting-segmentation-fault-139
- https://stackoverflow.com/questions/69336504/python3-8-10-source-build-with-error-makefile617-sharedmods-error-139
- https://stackoverflow.com/questions/42882168/how-to-solve-exit-code-139-error-when-reading-from-file-on-unix
- https://stackoverflow.com/questions/59099160/makefile586-recipe-for-target-sharedmods-failed
- https://www.linuxquestions.org/questions/linux-from-scratch-13/keep-getting-segmentation-faults-and-makefile-all-error-2-when-running-and-building-gcc-4-5-3-a-4175673166/
- https://github.com/kivy/python-for-android/issues/1474 (similar issue for python2 at https://github.com/kivy/python-for-android/issues/1297)
  - interesting discussion about fixes at https://github.com/kivy/python-for-android/pull/1460 and https://github.com/kivy/python-for-android/pull/1534
- https://github.com/kivy/python-for-android/issues/1337 then https://github.com/kivy/python-for-android/pull/1433 then https://github.com/kivy/python-for-android/pull/1624
  - related: https://github.com/kivy/python-for-android/pull/1517 and https://github.com/kivy/python-for-android/pull/1537

Links discussing the differences between `gcc` and `clang`:
- https://www.incredibuild.com/blog/gcc-vs-clang-battle-of-the-behemoths
- https://alibabatech.medium.com/gcc-vs-clang-llvm-an-in-depth-comparison-of-c-c-compilers-899ede2be378
- https://colfaxresearch.com/compiler-comparison/
-

Links discussing the difference between `double` versus `long double`:
- https://en.wikipedia.org/wiki/Long_double and https://en.wikipedia.org/wiki/Double-precision_floating-point_format
> Quoting from Wikipedia:
> > On the x86 architecture, most compilers implement long double as the 80-bit extended precision type supported by that hardware (sometimes stored as 12 or 16 bytes to maintain data structure .

> and
> > Compilers may also use long double for a 128-bit quadruple precision format, which is currently implemented in software.

> In other words, yes, a long double may be able to store a larger range of values than a double. But it's completely up to the compiler.

- https://stackoverflow.com/questions/68563245/long-double-vs-long-long
> > How is a long double same size as a double?

> Short and incomplete answer - because most current hardware only1 supports up to 64 bit words, which is the minimum necessary to meet the range and precision requirements for double. Once companies start regularly putting out hardware with larger word sizes, then you'll likely see larger sizes for long double.
- https://stackoverflow.com/questions/14221612/difference-between-long-double-and-double-in-c-and-c
- https://stackoverflow.com/questions/3454576/long-double-vs-double
- https://cplusplus.com/forum/beginner/252663/
- https://stackoverflow.com/questions/257353/whats-bigger-than-a-double
> C++ has long double, but there is no guarantee that it's any more precise than a plain double. On an x86 platform, usually double is 64 bits, and long double is either 64 or 80 bits (which gives you 19 significant figures, if I remember right).
> Your mileage may vary, especially if you're not on x86.

> A long double typically only uses 10 bytes, but due to alignment may actually take up 12 or 16 (depending on the compiler and options) bytes in a structure.
> The 10 byte long double provides a 64-bit mantissa; this is very convenient for when you want to store 64 bit integers in floating point without loss of precision.

> You can use [GNU MP](http://gmplib.org/). Its [floating-point functions](http://gmplib.org/manual/Floating_002dpoint-Functions.html#Floating_002dpoint-Functions) have unlimited mantissa and 32-bit or 64-bit (depending on the native word size) exponent. It also comes with a C++ wrapper.

#### stack trace for Docker image build failure

<details>
<summary><strong>stack trace for <code>Python-3.2.6</code> build failure</strong></summary>

<pre>
#6 1.722 checking for --enable-universalsdk... no
#6 1.723 checking for --with-universal-archs... 32-bit
#6 1.724 checking MACHDEP... linux2
#6 1.735 checking machine type as reported by uname -m... x86_64
#6 1.737 checking for --without-gcc... no
#6 1.738 checking for gcc... gcc
#6 1.773 checking whether the C compiler works... yes
#6 1.820 checking for C compiler default output file name... a.out
#6 1.822 checking for suffix of executables...
#6 1.869 checking whether we are cross compiling... no
#6 1.919 checking for suffix of object files... o
#6 1.947 checking whether we are using the GNU C compiler... yes
#6 1.974 checking whether gcc accepts -g... yes
#6 2.001 checking for gcc option to accept ISO C89... none needed
#6 2.036 checking for --with-cxx-main=<compiler>... no
#6 2.038 checking for g++... g++
#6 2.039 configure: WARNING:
#6 2.039
#6 2.039   By default, distutils will build C++ extension modules with "g++".
#6 2.039   If this is not intended, then set CXX on the configure command line.
#6 2.039
#6 2.039 checking for -Wl,--no-as-needed... yes
#6 2.088 checking how to run the C preprocessor... gcc -E
#6 2.156 checking for grep that handles long lines and -e... /bin/grep
#6 2.160 checking for egrep... /bin/grep -E
#6 2.163 checking for ANSI C header files... yes
#6 2.295 checking for sys/types.h... yes
#6 2.336 checking for sys/stat.h... yes
#6 2.378 checking for stdlib.h... yes
#6 2.420 checking for string.h... yes
#6 2.464 checking for memory.h... yes
#6 2.508 checking for strings.h... yes
#6 2.552 checking for inttypes.h... yes
#6 2.597 checking for stdint.h... yes
#6 2.642 checking for unistd.h... yes
#6 2.685 checking minix/config.h usability... no
#6 2.724 checking minix/config.h presence... no
#6 2.744 checking for minix/config.h... no
#6 2.745 checking whether it is safe to define __EXTENSIONS__... yes
#6 2.788 checking for --with-suffix...
#6 2.789 checking for case-insensitive build directory... no
#6 2.796 checking LIBRARY... libpython$(VERSION)$(ABIFLAGS).a
#6 2.797 checking LINKCC... $(PURIFY) $(MAINCC)
#6 2.797 checking for GNU ld... yes
#6 2.803 checking for inline... inline
#6 2.825 checking for --enable-shared... no
#6 2.825 checking for --enable-profiling...
#6 2.826 checking LDLIBRARY... libpython$(VERSION)$(ABIFLAGS).a
#6 2.827 checking for ranlib... ranlib
#6 2.828 checking for ar... ar
#6 2.829 checking for svnversion... not-found
#6 2.830 checking for python3.2... no
#6 2.831 checking for python3... no
#6 2.832 checking for python... no
#6 2.832 checking for a BSD-compatible install... /usr/bin/install -c
#6 2.846 checking for a thread-safe mkdir -p... /bin/mkdir -p
#6 2.850 checking for --with-pydebug... no
#6 2.865 checking whether gcc accepts and needs -fno-strict-aliasing... no
#6 2.918 checking whether gcc supports ParseTuple __format__... yes
#6 2.945 checking whether pthreads are available without options... no
#6 3.001 checking whether gcc accepts -Kpthread... no
#6 3.015 checking whether gcc accepts -Kthread... no
#6 3.028 checking whether gcc accepts -pthread... yes
#6 3.088 checking whether g++ also accepts flags for thread support... no
#6 3.092 checking for ANSI C header files... (cached) yes
#6 3.097 checking asm/types.h usability... yes
#6 3.134 checking asm/types.h presence... yes
#6 3.147 checking for asm/types.h... yes
#6 3.158 checking conio.h usability... no
#6 3.198 checking conio.h presence... no
#6 3.217 checking for conio.h... no
#6 3.222 checking curses.h usability... no
#6 3.261 checking curses.h presence... no
#6 3.281 checking for curses.h... no
#6 3.287 checking direct.h usability... no
#6 3.326 checking direct.h presence... no
#6 3.346 checking for direct.h... no
#6 3.352 checking dlfcn.h usability... yes
#6 3.389 checking dlfcn.h presence... yes
#6 3.404 checking for dlfcn.h... yes
#6 3.414 checking errno.h usability... yes
#6 3.453 checking errno.h presence... yes
#6 3.468 checking for errno.h... yes
#6 3.478 checking fcntl.h usability... yes
#6 3.517 checking fcntl.h presence... yes
#6 3.533 checking for fcntl.h... yes
#6 3.544 checking grp.h usability... yes
#6 3.582 checking grp.h presence... yes
#6 3.597 checking for grp.h... yes
#6 3.607 checking ieeefp.h usability... no
#6 3.646 checking ieeefp.h presence... no
#6 3.667 checking for ieeefp.h... no
#6 3.671 checking io.h usability... no
#6 3.711 checking io.h presence... no
#6 3.731 checking for io.h... no
#6 3.736 checking langinfo.h usability... yes
#6 3.775 checking langinfo.h presence... yes
#6 3.790 checking for langinfo.h... yes
#6 3.800 checking libintl.h usability... yes
#6 3.838 checking libintl.h presence... yes
#6 3.852 checking for libintl.h... yes
#6 3.863 checking ncurses.h usability... no
#6 3.902 checking ncurses.h presence... no
#6 3.922 checking for ncurses.h... no
#6 3.926 checking poll.h usability... yes
#6 3.965 checking poll.h presence... yes
#6 3.979 checking for poll.h... yes
#6 3.990 checking process.h usability... no
#6 4.029 checking process.h presence... no
#6 4.050 checking for process.h... no
#6 4.055 checking pthread.h usability... yes
#6 4.097 checking pthread.h presence... yes
#6 4.115 checking for pthread.h... yes
#6 4.125 checking shadow.h usability... yes
#6 4.163 checking shadow.h presence... yes
#6 4.178 checking for shadow.h... yes
#6 4.189 checking signal.h usability... yes
#6 4.231 checking signal.h presence... yes
#6 4.249 checking for signal.h... yes
#6 4.259 checking for stdint.h... (cached) yes
#6 4.269 checking stropts.h usability... no
#6 4.309 checking stropts.h presence... no
#6 4.329 checking for stropts.h... no
#6 4.334 checking termios.h usability... yes
#6 4.373 checking termios.h presence... yes
#6 4.388 checking for termios.h... yes
#6 4.398 checking thread.h usability... no
#6 4.438 checking thread.h presence... no
#6 4.458 checking for thread.h... no
#6 4.462 checking for unistd.h... (cached) yes
#6 4.473 checking utime.h usability... yes
#6 4.511 checking utime.h presence... yes
#6 4.526 checking for utime.h... yes
#6 4.536 checking sys/audioio.h usability... no
#6 4.575 checking sys/audioio.h presence... no
#6 4.595 checking for sys/audioio.h... no
#6 4.600 checking sys/bsdtty.h usability... no
#6 4.640 checking sys/bsdtty.h presence... no
#6 4.660 checking for sys/bsdtty.h... no
#6 4.665 checking sys/epoll.h usability... yes
#6 4.703 checking sys/epoll.h presence... yes
#6 4.720 checking for sys/epoll.h... yes
#6 4.730 checking sys/event.h usability... no
#6 4.769 checking sys/event.h presence... no
#6 4.789 checking for sys/event.h... no
#6 4.794 checking sys/file.h usability... yes
#6 4.832 checking sys/file.h presence... yes
#6 4.848 checking for sys/file.h... yes
#6 4.858 checking sys/loadavg.h usability... no
#6 4.898 checking sys/loadavg.h presence... no
#6 4.918 checking for sys/loadavg.h... no
#6 4.923 checking sys/lock.h usability... no
#6 4.962 checking sys/lock.h presence... no
#6 4.982 checking for sys/lock.h... no
#6 4.987 checking sys/mkdev.h usability... no
#6 5.027 checking sys/mkdev.h presence... no
#6 5.049 checking for sys/mkdev.h... no
#6 5.054 checking sys/modem.h usability... no
#6 5.092 checking sys/modem.h presence... no
#6 5.112 checking for sys/modem.h... no
#6 5.117 checking sys/param.h usability... yes
#6 5.159 checking sys/param.h presence... yes
#6 5.180 checking for sys/param.h... yes
#6 5.194 checking sys/poll.h usability... yes
#6 5.236 checking sys/poll.h presence... yes
#6 5.255 checking for sys/poll.h... yes
#6 5.265 checking sys/select.h usability... yes
#6 5.302 checking sys/select.h presence... yes
#6 5.317 checking for sys/select.h... yes
#6 5.328 checking sys/socket.h usability... yes
#6 5.368 checking sys/socket.h presence... yes
#6 5.386 checking for sys/socket.h... yes
#6 5.397 checking sys/statvfs.h usability... yes
#6 5.435 checking sys/statvfs.h presence... yes
#6 5.449 checking for sys/statvfs.h... yes
#6 5.459 checking for sys/stat.h... (cached) yes
#6 5.469 checking sys/syscall.h usability... yes
#6 5.509 checking sys/syscall.h presence... yes
#6 5.523 checking for sys/syscall.h... yes
#6 5.533 checking sys/termio.h usability... no
#6 5.572 checking sys/termio.h presence... no
#6 5.592 checking for sys/termio.h... no
#6 5.597 checking sys/time.h usability... yes
#6 5.635 checking sys/time.h presence... yes
#6 5.650 checking for sys/time.h... yes
#6 5.661 checking sys/times.h usability... yes
#6 5.698 checking sys/times.h presence... yes
#6 5.713 checking for sys/times.h... yes
#6 5.723 checking for sys/types.h... (cached) yes
#6 5.734 checking sys/un.h usability... yes
#6 5.771 checking sys/un.h presence... yes
#6 5.787 checking for sys/un.h... yes
#6 5.798 checking sys/utsname.h usability... yes
#6 5.835 checking sys/utsname.h presence... yes
#6 5.849 checking for sys/utsname.h... yes
#6 5.860 checking sys/wait.h usability... yes
#6 5.901 checking sys/wait.h presence... yes
#6 5.919 checking for sys/wait.h... yes
#6 5.929 checking pty.h usability... yes
#6 5.968 checking pty.h presence... yes
#6 5.984 checking for pty.h... yes
#6 5.995 checking libutil.h usability... no
#6 6.036 checking libutil.h presence... no
#6 6.057 checking for libutil.h... no
#6 6.062 checking sys/resource.h usability... yes
#6 6.100 checking sys/resource.h presence... yes
#6 6.115 checking for sys/resource.h... yes
#6 6.125 checking netpacket/packet.h usability... yes
#6 6.164 checking netpacket/packet.h presence... yes
#6 6.178 checking for netpacket/packet.h... yes
#6 6.189 checking sysexits.h usability... yes
#6 6.227 checking sysexits.h presence... yes
#6 6.240 checking for sysexits.h... yes
#6 6.250 checking bluetooth.h usability... no
#6 6.290 checking bluetooth.h presence... no
#6 6.310 checking for bluetooth.h... no
#6 6.317 checking bluetooth/bluetooth.h usability... no
#6 6.356 checking bluetooth/bluetooth.h presence... no
#6 6.376 checking for bluetooth/bluetooth.h... no
#6 6.381 checking linux/tipc.h usability... yes
#6 6.420 checking linux/tipc.h presence... yes
#6 6.434 checking for linux/tipc.h... yes
#6 6.444 checking spawn.h usability... yes
#6 6.483 checking spawn.h presence... yes
#6 6.500 checking for spawn.h... yes
#6 6.511 checking util.h usability... no
#6 6.550 checking util.h presence... no
#6 6.571 checking for util.h... no
#6 6.576 checking for dirent.h that defines DIR... yes
#6 6.613 checking for library containing opendir... none required
#6 6.663 checking whether sys/types.h defines makedev... no
#6 6.721 checking for sys/mkdev.h... (cached) no
#6 6.722 checking sys/sysmacros.h usability... yes
#6 6.762 checking sys/sysmacros.h presence... yes
#6 6.776 checking for sys/sysmacros.h... yes
#6 6.777 checking for term.h... no
#6 6.800 checking for linux/netlink.h... yes
#6 6.830 checking for clock_t in time.h... yes
#6 6.846 checking for makedev... yes
#6 6.896 checking Solaris LFS bug... no
#6 6.926 checking for mode_t... yes
#6 7.010 checking for off_t... yes
#6 7.096 checking for pid_t... yes
#6 7.183 checking for size_t... yes
#6 7.266 checking for uid_t in sys/types.h... yes
#6 7.283 checking for uint32_t... yes
#6 7.368 checking for uint32_t... yes
#6 7.412 checking for uint64_t... yes
#6 7.496 checking for uint64_t... yes
#6 7.541 checking for int32_t... yes
#6 7.624 checking for int32_t... yes
#6 7.708 checking for int64_t... yes
#6 7.792 checking for int64_t... yes
#6 7.876 checking for ssize_t... yes
#6 7.959 checking size of int... 4
#6 8.030 checking size of long... 8
#6 8.102 checking size of void *... 8
#6 8.172 checking size of short... 2
#6 8.245 checking size of float... 4
#6 8.316 checking size of double... 8
#6 8.387 checking size of fpos_t... 16
#6 8.459 checking size of size_t... 8
#6 8.530 checking size of pid_t... 4
#6 8.600 checking for long long support... yes
#6 8.627 checking size of long long... 8
#6 8.698 checking for long double support... yes
#6 8.725 checking size of long double... 16
#6 8.797 checking for _Bool support... yes
#6 8.824 checking size of _Bool... 1
#6 8.894 checking for uintptr_t... yes
#6 8.950 checking size of uintptr_t... 8
#6 9.021 checking size of off_t... 8
#6 9.087 checking whether to enable large file support... no
#6 9.087 checking size of time_t... 8
#6 9.152 checking for pthread_t... yes
#6 9.185 checking size of pthread_t... 8
#6 9.253 checking for --enable-framework... no
#6 9.253 checking for dyld... no
#6 9.254 checking the extension of shared libraries... .so
#6 9.254 checking LDSHARED... $(CC) -shared
#6 9.255 checking CCSHARED... -fPIC
#6 9.255 checking LINKFORSHARED... -Xlinker -export-dynamic
#6 9.256 checking CFLAGSFORSHARED...
#6 9.256 checking SHLIBS... $(LIBS)
#6 9.257 checking for dlopen in -ldl... yes
#6 9.308 checking for shl_load in -ldld... no
#6 9.350 checking for library containing sem_init... -lpthread
#6 9.454 checking for textdomain in -lintl... no
#6 9.497 checking for t_open in -lnsl... no
#6 9.554 checking for socket in -lsocket... no
#6 9.579 checking for --with-libs... no
#6 9.579 checking for pkg-config... no
#6 9.581 checking for --with-system-expat... no
#6 9.581 checking for --with-system-ffi... no
#6 9.581 checking for --enable-loadable-sqlite-extensions... no
#6 9.581 checking for --with-dbmliborder...
#6 9.581 checking for --with-signal-module... yes
#6 9.582 checking for --with-dec-threads... no
#6 9.582 checking for --with-threads... yes
#6 9.583 checking if PTHREAD_SCOPE_SYSTEM is supported... yes
#6 9.642 checking for pthread_sigmask... yes
#6 9.696 checking if --enable-ipv6 is specified... yes
#6 9.729 checking if RFC2553 API is available... yes
#6 9.764 checking ipv6 stack type... linux-glibc
#6 9.817 checking for OSX 10.5 SDK or later... no
#6 9.840 checking for --with-doc-strings... yes
#6 9.841 checking for --with-tsc... no
#6 9.841 checking for --with-pymalloc... yes
#6 9.841 checking for --with-valgrind... no
#6 9.842 checking for dlopen... yes
#6 9.895 checking DYNLOADFILE... dynload_shlib.o
#6 9.896 checking MACHDEP_OBJS... MACHDEP_OBJS
#6 9.901 checking for alarm... yes
#6 9.962 checking for accept4... yes
#6 10.03 checking for setitimer... yes
#6 10.13 checking for getitimer... yes
#6 10.19 checking for bind_textdomain_codeset... yes
#6 10.25 checking for chown... yes
#6 10.31 checking for clock... yes
#6 10.37 checking for confstr... yes
#6 10.44 checking for ctermid... yes
#6 10.50 checking for execv... yes
#6 10.56 checking for fchmod... yes
#6 10.63 checking for fchown... yes
#6 10.69 checking for fork... yes
#6 10.75 checking for fpathconf... yes
#6 10.82 checking for ftime... yes
#6 10.88 checking for ftruncate... yes
#6 10.94 checking for gai_strerror... yes
#6 11.00 checking for getgroups... yes
#6 11.06 checking for getlogin... yes
#6 11.12 checking for getloadavg... yes
#6 11.19 checking for getpeername... yes
#6 11.25 checking for getpgid... yes
#6 11.31 checking for getpid... yes
#6 11.37 checking for getpriority... yes
#6 11.43 checking for getresuid... yes
#6 11.49 checking for getresgid... yes
#6 11.55 checking for getpwent... yes
#6 11.61 checking for getspnam... yes
#6 11.68 checking for getspent... yes
#6 11.74 checking for getsid... yes
#6 11.80 checking for getwd... yes
#6 11.86 checking for initgroups... yes
#6 11.93 checking for kill... yes
#6 11.99 checking for killpg... yes
#6 12.05 checking for lchmod... no
#6 12.08 checking for lchown... yes
#6 12.14 checking for lstat... yes
#6 12.21 checking for mbrtowc... yes
#6 12.27 checking for mkfifo... yes
#6 12.33 checking for mknod... yes
#6 12.39 checking for mktime... yes
#6 12.45 checking for mremap... yes
#6 12.52 checking for nice... yes
#6 12.58 checking for pathconf... yes
#6 12.64 checking for pause... yes
#6 12.70 checking for plock... no
#6 12.76 checking for poll... yes
#6 12.82 checking for pthread_init... no
#6 12.89 checking for putenv... yes
#6 12.95 checking for readlink... yes
#6 13.01 checking for realpath... yes
#6 13.07 checking for select... yes
#6 13.13 checking for sem_open... yes
#6 13.20 checking for sem_timedwait... yes
#6 13.26 checking for sem_getvalue... yes
#6 13.32 checking for sem_unlink... yes
#6 13.38 checking for setegid... yes
#6 13.44 checking for seteuid... yes
#6 13.50 checking for setgid... yes
#6 13.56 checking for setlocale... yes
#6 13.63 checking for setregid... yes
#6 13.69 checking for setreuid... yes
#6 13.75 checking for setresuid... yes
#6 13.81 checking for setresgid... yes
#6 13.87 checking for setsid... yes
#6 13.93 checking for setpgid... yes
#6 14.00 checking for setpgrp... yes
#6 14.06 checking for setuid... yes
#6 14.12 checking for setvbuf... yes
#6 14.18 checking for sigaction... yes
#6 14.24 checking for siginterrupt... yes
#6 14.31 checking for sigrelse... yes
#6 14.37 checking for snprintf... yes
#6 14.43 checking for strftime... yes
#6 14.50 checking for strlcpy... no
#6 14.56 checking for sysconf... yes
#6 14.62 checking for tcgetpgrp... yes
#6 14.69 checking for tcsetpgrp... yes
#6 14.75 checking for tempnam... yes
#6 14.81 checking for timegm... yes
#6 14.87 checking for times... yes
#6 14.93 checking for tmpfile... yes
#6 15.00 checking for tmpnam... yes
#6 15.06 checking for tmpnam_r... yes
#6 15.13 checking for truncate... yes
#6 15.19 checking for uname... yes
#6 15.26 checking for unsetenv... yes
#6 15.32 checking for utimes... yes
#6 15.38 checking for waitpid... yes
#6 15.44 checking for wait3... yes
#6 15.50 checking for wait4... yes
#6 15.56 checking for wcscoll... yes
#6 15.62 checking for wcsftime... yes
#6 15.68 checking for wcsxfrm... yes
#6 15.75 checking for _getpty... no
#6 15.81 checking whether dirfd is declared... yes
#6 15.84 checking for chroot... yes
#6 15.88 checking for link... yes
#6 15.91 checking for symlink... yes
#6 15.94 checking for fchdir... yes
#6 15.97 checking for fsync... yes
#6 16.00 checking for fdatasync... yes
#6 16.03 checking for epoll... yes
#6 16.07 checking for kqueue... no
#6 16.09 checking for ctermid_r... no
#6 16.12 checking for flock declaration... yes
#6 16.15 checking for flock... yes
#6 16.21 checking for getpagesize... yes
#6 16.24 checking for broken unsetenv... no
#6 16.27 checking for true... true
#6 16.28 checking for inet_aton in -lc... yes
#6 16.33 checking for chflags... no
#6 16.39 checking for lchflags... no
#6 16.45 checking for inflateCopy in -lz... no
#6 16.49 checking for hstrerror... yes
#6 16.55 checking for inet_aton... yes
#6 16.61 checking for inet_pton... yes
#6 16.64 checking for setgroups... yes
#6 16.67 checking for openpty... no
#6 16.73 checking for openpty in -lutil... yes
#6 16.78 checking for forkpty... yes
#6 16.84 checking for memmove... yes
#6 16.90 checking for fseek64... no
#6 16.96 checking for fseeko... yes
#6 17.03 checking for fstatvfs... yes
#6 17.09 checking for ftell64... no
#6 17.15 checking for ftello... yes
#6 17.21 checking for statvfs... yes
#6 17.27 checking for dup2... yes
#6 17.32 checking for getcwd... yes
#6 17.37 checking for strdup... yes
#6 17.43 checking for getpgrp... yes
#6 17.51 checking for setpgrp... (cached) yes
#6 17.54 checking for gettimeofday... yes
#6 17.62 checking for major... yes
#6 17.68 checking for getaddrinfo... yes
#6 17.74 checking getaddrinfo bug... no
#6 17.80 checking for getnameinfo... yes
#6 17.86 checking whether time.h and sys/time.h may both be included... yes
#6 17.89 checking whether struct tm is in sys/time.h or time.h... time.h
#6 17.92 checking for struct tm.tm_zone... yes
#6 17.95 checking for struct stat.st_rdev... yes
#6 18.00 checking for struct stat.st_blksize... yes
#6 18.05 checking for struct stat.st_flags... no
#6 18.13 checking for struct stat.st_gen... no
#6 18.21 checking for struct stat.st_birthtime... no
#6 18.29 checking for struct stat.st_blocks... yes
#6 18.34 checking for time.h that defines altzone... no
#6 18.37 checking whether sys/select.h and sys/time.h may both be included... yes
#6 18.40 checking for addrinfo... yes
#6 18.43 checking for sockaddr_storage... yes
#6 18.47 checking whether char is unsigned... no
#6 18.51 checking for an ANSI C-conforming const... yes
#6 18.54 checking for working volatile... yes
#6 18.57 checking for working signed char... yes
#6 18.60 checking for prototypes... yes
#6 18.62 checking for variable length prototypes and stdarg.h... yes
#6 18.65 checking for socketpair... yes
#6 18.69 checking if sockaddr has sa_len member... no
#6 18.72 checking whether va_list is an array... yes
#6 18.74 checking for gethostbyname_r... yes
#6 18.79 checking gethostbyname_r with 6 args... yes
#6 18.83 checking for __fpu_control... yes
#6 18.88 checking for --with-fpectl... no
#6 18.88 checking for --with-libm=STRING... default LIBM="-lm"
#6 18.88 checking for --with-libc=STRING... default LIBC=""
#6 18.88 checking whether C doubles are little-endian IEEE 754 binary64... yes
#6 18.94 checking whether C doubles are big-endian IEEE 754 binary64... no
#6 18.99 checking whether C doubles are ARM mixed-endian IEEE 754 binary64... no
#6 19.05 checking whether we can use gcc inline assembler to get and set x87 control word... yes
#6 19.08 checking for x87-style double rounding... no
#6 19.17 checking for acosh... yes
#6 19.24 checking for asinh... yes
#6 19.31 checking for atanh... yes
#6 19.39 checking for copysign... yes
#6 19.46 checking for erf... yes
#6 19.54 checking for erfc... yes
#6 19.61 checking for expm1... yes
#6 19.68 checking for finite... yes
#6 19.76 checking for gamma... yes
#6 19.83 checking for hypot... yes
#6 19.91 checking for lgamma... yes
#6 19.98 checking for log1p... yes
#6 20.06 checking for round... yes
#6 20.13 checking for tgamma... yes
#6 20.21 checking whether isinf is declared... yes
#6 20.27 checking whether isnan is declared... yes
#6 20.33 checking whether isfinite is declared... yes
#6 20.39 checking whether tanh preserves the sign of zero... yes
#6 20.47 checking whether log1p drops the sign of negative zero... no
#6 20.55 checking whether POSIX semaphores are enabled... yes
#6 20.62 checking for broken sem_getvalue... no
#6 20.68 checking digit size for Python's longs... no value specified
#6 20.69 checking wchar.h usability... yes
#6 20.73 checking wchar.h presence... yes
#6 20.74 checking for wchar.h... yes
#6 20.74 checking size of wchar_t... 4
#6 20.81 checking for UCS-4 tcl... no
#6 20.83 checking whether wchar_t is signed... yes
#6 20.89 checking what type to use for str... unsigned short
#6 20.89 checking whether byte ordering is bigendian... no
#6 20.98 checking ABIFLAGS... m
#6 20.98 checking SOABI... cpython-32m
#6 20.98 checking LDVERSION... $(VERSION)$(ABIFLAGS)
#6 20.98 checking whether right shift extends the sign bit... yes
#6 21.04 checking for getc_unlocked() and friends... yes
#6 21.09 checking how to link readline libs... none
#6 21.31 checking for rl_callback_handler_install in -lreadline... no
#6 21.37 checking for rl_pre_input_hook in -lreadline... no
#6 21.42 checking for rl_completion_display_matches_hook in -lreadline... no
#6 21.47 checking for rl_completion_matches in -lreadline... no
#6 21.53 checking for broken nice()... no
#6 21.58 checking for broken poll()... no
#6 21.64 checking for struct tm.tm_zone... (cached) yes
#6 21.64 checking for working tzset()... yes
#6 21.71 checking for tv_nsec in struct stat... yes
#6 21.74 checking for tv_nsec2 in struct stat... no
#6 21.77 checking whether mvwdelch is an expression... no
#6 21.79 checking whether WINDOW has _flags... no
#6 21.81 checking for is_term_resized... no
#6 21.84 checking for resize_term... no
#6 21.86 checking for resizeterm... no
#6 21.88 checking for /dev/ptmx... yes
#6 21.88 checking for /dev/ptc... no
#6 21.88 checking for %lld and %llu printf() format support... yes
#6 21.94 checking for %zd printf() format support... yes
#6 22.00 checking for socklen_t... yes
#6 22.07 checking for broken mbstowcs... no
#6 22.13 checking whether gcc -pthread supports computed gotos... yes
#6 22.18 checking for --with-computed-gotos... no value specified
#6 22.18 checking for pipe2... yes
#6 22.23 checking for build directories... done
#6 22.27 configure: creating ./config.status
#6 22.40 config.status: creating Makefile.pre
#6 22.41 config.status: creating Modules/Setup.config
#6 22.44 config.status: creating Misc/python.pc
#6 22.46 config.status: creating Modules/ld_so_aix
#6 22.49 config.status: creating pyconfig.h
#6 22.50 creating Modules/Setup
#6 22.50 creating Modules/Setup.local
#6 22.50 creating Makefile
#6 22.68 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Modules/python.o ./Modules/python.c
#6 22.74 In file included from Include/Python.h:110,
#6 22.74                  from ./Modules/python.c:3:
#6 22.74 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 22.74    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 22.74       | ^~~~~~~~~~
#6 22.78 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/acceler.o Parser/acceler.c
#6 22.85 In file included from Include/Python.h:110,
#6 22.85                  from Include/pgenheaders.h:10,
#6 22.85                  from Parser/acceler.c:13:
#6 22.85 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 22.85    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 22.85       | ^~~~~~~~~~
#6 22.92 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/grammar1.o Parser/grammar1.c
#6 22.99 In file included from Include/Python.h:110,
#6 22.99                  from Parser/grammar1.c:4:
#6 22.99 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 22.99    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 22.99       | ^~~~~~~~~~
#6 23.02 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/listnode.o Parser/listnode.c
#6 23.08 In file included from Include/Python.h:110,
#6 23.08                  from Include/pgenheaders.h:10,
#6 23.08                  from Parser/listnode.c:4:
#6 23.08 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 23.08    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 23.08       | ^~~~~~~~~~
#6 23.20 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/node.o Parser/node.c
#6 23.27 In file included from Include/Python.h:110,
#6 23.27                  from Parser/node.c:3:
#6 23.27 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 23.27    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 23.27       | ^~~~~~~~~~
#6 23.39 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/parser.o Parser/parser.c
#6 23.45 In file included from Include/Python.h:110,
#6 23.45                  from Parser/parser.c:8:
#6 23.45 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 23.45    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 23.45       | ^~~~~~~~~~
#6 23.53 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/parsetok.o Parser/parsetok.c
#6 23.60 In file included from Include/Python.h:110,
#6 23.60                  from Include/pgenheaders.h:10,
#6 23.60                  from Parser/parsetok.c:4:
#6 23.60 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 23.60    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 23.60       | ^~~~~~~~~~
#6 23.71 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/bitset.o Parser/bitset.c
#6 23.78 In file included from Include/Python.h:110,
#6 23.78                  from Include/pgenheaders.h:10,
#6 23.78                  from Parser/bitset.c:4:
#6 23.78 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 23.78    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 23.78       | ^~~~~~~~~~
#6 23.83 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/metagrammar.o Parser/metagrammar.c
#6 23.90 In file included from Include/Python.h:110,
#6 23.90                  from Include/pgenheaders.h:10,
#6 23.90                  from Parser/metagrammar.c:2:
#6 23.90 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 23.90    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 23.90       | ^~~~~~~~~~
#6 23.92 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/firstsets.o Parser/firstsets.c
#6 23.98 In file included from Include/Python.h:110,
#6 23.98                  from Include/pgenheaders.h:10,
#6 23.98                  from Parser/firstsets.c:4:
#6 23.98 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 23.98    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 23.98       | ^~~~~~~~~~
#6 24.05 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/grammar.o Parser/grammar.c
#6 24.11 In file included from Include/Python.h:110,
#6 24.11                  from Parser/grammar.c:4:
#6 24.11 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 24.11    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 24.11       | ^~~~~~~~~~
#6 24.22 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/pgen.o Parser/pgen.c
#6 24.28 In file included from Include/Python.h:110,
#6 24.28                  from Parser/pgen.c:5:
#6 24.28 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 24.28    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 24.28       | ^~~~~~~~~~
#6 24.29 Parser/pgen.c: In function 'compile_atom':
#6 24.29 Parser/pgen.c:282:9: warning: variable 'i' set but not used [-Wunused-but-set-variable]
#6 24.29   282 |     int i;
#6 24.29       |         ^
#6 24.64 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/myreadline.o Parser/myreadline.c
#6 24.71 In file included from Include/Python.h:110,
#6 24.71                  from Parser/myreadline.c:12:
#6 24.71 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 24.71    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 24.71       | ^~~~~~~~~~
#6 24.76 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/tokenizer.o Parser/tokenizer.c
#6 24.83 In file included from Include/Python.h:110,
#6 24.83                  from Parser/tokenizer.c:4:
#6 24.83 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 24.83    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 24.83       | ^~~~~~~~~~
#6 25.34 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/abstract.o Objects/abstract.c
#6 25.41 In file included from Include/Python.h:110,
#6 25.41                  from Objects/abstract.c:3:
#6 25.41 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 25.41    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 25.41       | ^~~~~~~~~~
#6 27.01 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/accu.o Objects/accu.c
#6 27.08 In file included from Include/Python.h:110,
#6 27.08                  from Objects/accu.c:3:
#6 27.08 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 27.08    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 27.08       | ^~~~~~~~~~
#6 27.15 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/boolobject.o Objects/boolobject.c
#6 27.22 In file included from Include/Python.h:110,
#6 27.22                  from Objects/boolobject.c:3:
#6 27.22 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 27.22    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 27.22       | ^~~~~~~~~~
#6 27.27 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/bytes_methods.o Objects/bytes_methods.c
#6 27.34 In file included from Include/Python.h:110,
#6 27.34                  from Objects/bytes_methods.c:1:
#6 27.34 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 27.34    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 27.34       | ^~~~~~~~~~
#6 27.49 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/bytearrayobject.o Objects/bytearrayobject.c
#6 27.55 In file included from Include/Python.h:110,
#6 27.55                  from Objects/bytearrayobject.c:4:
#6 27.55 Include/modsupport.h:27:1: warning: '_PyArg_ParseTuple_SizeT' is an unrecognized format function type [-Wformat=]
#6 27.55    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 27.55       | ^~~~~~~~~~
#6 29.31 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/bytesobject.o Objects/bytesobject.c
#6 29.37 In file included from Include/Python.h:110,
#6 29.37                  from Objects/bytesobject.c:5:
#6 29.37 Include/modsupport.h:27:1: warning: '_PyArg_ParseTuple_SizeT' is an unrecognized format function type [-Wformat=]
#6 29.37    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 29.37       | ^~~~~~~~~~
#6 29.38 In file included from Include/Python.h:68,
#6 29.38                  from Objects/bytesobject.c:5:
#6 29.38 Objects/bytesobject.c: In function 'PyBytes_FromStringAndSize':
#6 29.38 Include/objimpl.h:161:66: warning: right-hand operand of comma expression has no effect [-Wunused-value]
#6 29.38   161 |     ( Py_TYPE(op) = (typeobj), _Py_NewReference((PyObject *)(op)), (op) )
#6 29.38       |     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^~~~~~~~
#6 29.38 Include/objimpl.h:163:29: note: in expansion of macro 'PyObject_INIT'
#6 29.38   163 |     ( Py_SIZE(op) = (size), PyObject_INIT((op), (typeobj)) )
#6 29.38       |                             ^~~~~~~~~~~~~
#6 29.38 Objects/bytesobject.c:105:5: note: in expansion of macro 'PyObject_INIT_VAR'
#6 29.38   105 |     PyObject_INIT_VAR(op, &PyBytes_Type, size);
#6 29.38       |     ^~~~~~~~~~~~~~~~~
#6 29.38 Objects/bytesobject.c: In function 'PyBytes_FromString':
#6 29.38 Include/objimpl.h:161:66: warning: right-hand operand of comma expression has no effect [-Wunused-value]
#6 29.38   161 |     ( Py_TYPE(op) = (typeobj), _Py_NewReference((PyObject *)(op)), (op) )
#6 29.38       |     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^~~~~~~~
#6 29.38 Include/objimpl.h:163:29: note: in expansion of macro 'PyObject_INIT'
#6 29.38   163 |     ( Py_SIZE(op) = (size), PyObject_INIT((op), (typeobj)) )
#6 29.38       |                             ^~~~~~~~~~~~~
#6 29.38 Objects/bytesobject.c:153:5: note: in expansion of macro 'PyObject_INIT_VAR'
#6 29.38   153 |     PyObject_INIT_VAR(op, &PyBytes_Type, size);
#6 29.38       |     ^~~~~~~~~~~~~~~~~
#6 29.39 Objects/bytesobject.c: In function 'bytes_repeat':
#6 29.39 Include/objimpl.h:161:66: warning: right-hand operand of comma expression has no effect [-Wunused-value]
#6 29.39   161 |     ( Py_TYPE(op) = (typeobj), _Py_NewReference((PyObject *)(op)), (op) )
#6 29.39       |     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^~~~~~~~
#6 29.39 Include/objimpl.h:163:29: note: in expansion of macro 'PyObject_INIT'
#6 29.39   163 |     ( Py_SIZE(op) = (size), PyObject_INIT((op), (typeobj)) )
#6 29.39       |                             ^~~~~~~~~~~~~
#6 29.39 Objects/bytesobject.c:752:5: note: in expansion of macro 'PyObject_INIT_VAR'
#6 29.39   752 |     PyObject_INIT_VAR(op, &PyBytes_Type, size);
#6 29.39       |     ^~~~~~~~~~~~~~~~~
#6 31.25 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/cellobject.o Objects/cellobject.c
#6 31.32 In file included from Include/Python.h:110,
#6 31.32                  from Objects/cellobject.c:3:
#6 31.32 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 31.32    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 31.32       | ^~~~~~~~~~
#6 31.38 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/classobject.o Objects/classobject.c
#6 31.45 In file included from Include/Python.h:110,
#6 31.45                  from Objects/classobject.c:3:
#6 31.45 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 31.45    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 31.45       | ^~~~~~~~~~
#6 31.45 In file included from Include/Python.h:68,
#6 31.45                  from Objects/classobject.c:3:
#6 31.45 Objects/classobject.c: In function 'PyMethod_New':
#6 31.45 Include/objimpl.h:161:66: warning: right-hand operand of comma expression has no effect [-Wunused-value]
#6 31.45   161 |     ( Py_TYPE(op) = (typeobj), _Py_NewReference((PyObject *)(op)), (op) )
#6 31.45       |     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^~~~~~~~
#6 31.45 Objects/classobject.c:53:9: note: in expansion of macro 'PyObject_INIT'
#6 31.45    53 |         PyObject_INIT(im, &PyMethod_Type);
#6 31.45       |         ^~~~~~~~~~~~~
#6 31.64 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/codeobject.o Objects/codeobject.c
#6 31.71 In file included from Include/Python.h:110,
#6 31.71                  from Objects/codeobject.c:1:
#6 31.71 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 31.71    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 31.71       | ^~~~~~~~~~
#6 31.90 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/complexobject.o Objects/complexobject.c
#6 31.96 In file included from Include/Python.h:110,
#6 31.96                  from Objects/complexobject.c:8:
#6 31.96 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 31.96    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 31.96       | ^~~~~~~~~~
#6 31.97 In file included from Include/Python.h:68,
#6 31.97                  from Objects/complexobject.c:8:
#6 31.97 Objects/complexobject.c: In function 'PyComplex_FromCComplex':
#6 31.97 Include/objimpl.h:161:66: warning: right-hand operand of comma expression has no effect [-Wunused-value]
#6 31.97   161 |     ( Py_TYPE(op) = (typeobj), _Py_NewReference((PyObject *)(op)), (op) )
#6 31.97       |     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^~~~~~~~
#6 31.97 Objects/complexobject.c:220:5: note: in expansion of macro 'PyObject_INIT'
#6 31.97   220 |     PyObject_INIT(op, &PyComplex_Type);
#6 31.97       |     ^~~~~~~~~~~~~
#6 32.39 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/descrobject.o Objects/descrobject.c
#6 32.45 In file included from Include/Python.h:110,
#6 32.45                  from Objects/descrobject.c:3:
#6 32.45 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 32.45    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 32.45       | ^~~~~~~~~~
#6 32.84 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/enumobject.o Objects/enumobject.c
#6 32.90 In file included from Include/Python.h:110,
#6 32.90                  from Objects/enumobject.c:3:
#6 32.90 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 32.90    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 32.90       | ^~~~~~~~~~
#6 33.00 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/exceptions.o Objects/exceptions.c
#6 33.07 In file included from Include/Python.h:110,
#6 33.07                  from Objects/exceptions.c:8:
#6 33.07 Include/modsupport.h:27:1: warning: '_PyArg_ParseTuple_SizeT' is an unrecognized format function type [-Wformat=]
#6 33.07    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 33.07       | ^~~~~~~~~~
#6 33.84 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/genobject.o Objects/genobject.c
#6 33.90 In file included from Include/Python.h:110,
#6 33.90                  from Objects/genobject.c:3:
#6 33.90 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 33.90    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 33.90       | ^~~~~~~~~~
#6 34.08 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/fileobject.o Objects/fileobject.c
#6 34.14 In file included from Include/Python.h:110,
#6 34.14                  from Objects/fileobject.c:4:
#6 34.14 Include/modsupport.h:27:1: warning: '_PyArg_ParseTuple_SizeT' is an unrecognized format function type [-Wformat=]
#6 34.14    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 34.14       | ^~~~~~~~~~
#6 34.28 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/floatobject.o Objects/floatobject.c
#6 34.34 In file included from Include/Python.h:110,
#6 34.34                  from Objects/floatobject.c:7:
#6 34.34 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 34.34    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 34.34       | ^~~~~~~~~~
#6 34.35 In file included from Include/Python.h:68,
#6 34.35                  from Objects/floatobject.c:7:
#6 34.35 Objects/floatobject.c: In function 'PyFloat_FromDouble':
#6 34.35 Include/objimpl.h:161:66: warning: right-hand operand of comma expression has no effect [-Wunused-value]
#6 34.35   161 |     ( Py_TYPE(op) = (typeobj), _Py_NewReference((PyObject *)(op)), (op) )
#6 34.35       |     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^~~~~~~~
#6 34.35 Objects/floatobject.c:167:5: note: in expansion of macro 'PyObject_INIT'
#6 34.35   167 |     PyObject_INIT(op, &PyFloat_Type);
#6 34.35       |     ^~~~~~~~~~~~~
#6 35.16 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/frameobject.o Objects/frameobject.c
#6 35.23 In file included from Include/Python.h:110,
#6 35.23                  from Objects/frameobject.c:3:
#6 35.23 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 35.23    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 35.23       | ^~~~~~~~~~
#6 35.52 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/funcobject.o Objects/funcobject.c
#6 35.59 In file included from Include/Python.h:110,
#6 35.59                  from Objects/funcobject.c:4:
#6 35.59 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 35.59    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 35.59       | ^~~~~~~~~~
#6 35.85 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/iterobject.o Objects/iterobject.c
#6 35.91 In file included from Include/Python.h:110,
#6 35.91                  from Objects/iterobject.c:3:
#6 35.91 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 35.91    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 35.91       | ^~~~~~~~~~
#6 35.99 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/listobject.o Objects/listobject.c
#6 36.06 In file included from Include/Python.h:110,
#6 36.06                  from Objects/listobject.c:3:
#6 36.06 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 36.06    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 36.06       | ^~~~~~~~~~
#6 36.06 In file included from Include/Python.h:65,
#6 36.06                  from Objects/listobject.c:3:
#6 36.06 Objects/listobject.c: In function 'list_resize':
#6 36.06 Include/pymem.h:110:34: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#6 36.06   110 |  (type *) PyMem_REALLOC((p), (n) * sizeof(type)) )
#6 36.06       |                                  ^
#6 36.06 Include/pymem.h:77:21: note: in definition of macro 'PyMem_REALLOC'
#6 36.06    77 |     : realloc((p), (n) ? (n) : 1))
#6 36.06       |                     ^
#6 36.06 Objects/listobject.c:63:9: note: in expansion of macro 'PyMem_RESIZE'
#6 36.06    63 |         PyMem_RESIZE(items, PyObject *, new_allocated);
#6 36.06       |         ^~~~~~~~~~~~
#6 36.08 Objects/listobject.c: In function 'listsort':
#6 36.08 Objects/listobject.c:1926:52: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#6 36.08  1926 |             keys = PyMem_MALLOC(sizeof(PyObject *) * saved_ob_size);
#6 36.08 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#6 36.08    75 |     : malloc((n) ? (n) : 1))
#6 36.08       |               ^
#6 36.08 Objects/listobject.c: In function 'list_ass_subscript':
#6 36.09 Objects/listobject.c:2474:41: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#6 36.09  2474 |                 PyMem_MALLOC(slicelength*sizeof(PyObject*));
#6 36.09 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#6 36.09    75 |     : malloc((n) ? (n) : 1))
#6 36.09       |               ^
#6 36.09 Objects/listobject.c:2555:41: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#6 36.09  2555 |                 PyMem_MALLOC(slicelength*sizeof(PyObject*));
#6 36.09 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#6 36.09    75 |     : malloc((n) ? (n) : 1))
#6 36.09       |               ^
#6 37.16 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/longobject.o Objects/longobject.c
#6 37.23 In file included from Include/Python.h:110,
#6 37.23                  from Objects/longobject.c:5:
#6 37.23 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 37.23    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 37.23       | ^~~~~~~~~~
#6 37.29 In file included from Include/Python.h:68,
#6 37.29                  from Objects/longobject.c:5:
#6 37.29 Objects/longobject.c: In function '_PyLong_Init':
#6 37.29 Include/objimpl.h:161:66: warning: right-hand operand of comma expression has no effect [-Wunused-value]
#6 37.29   161 |     ( Py_TYPE(op) = (typeobj), _Py_NewReference((PyObject *)(op)), (op) )
#6 37.29       |     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^~~~~~~~
#6 37.29 Objects/longobject.c:4899:13: note: in expansion of macro 'PyObject_INIT'
#6 37.29  4899 |             PyObject_INIT(v, &PyLong_Type);
#6 37.29       |             ^~~~~~~~~~~~~
#6 39.11 Objects/longobject.c: In function '_PyLong_Frexp':
#6 39.11 Objects/longobject.c:2468:33: warning: 'x_digits[0]' may be used uninitialized in this function [-Wmaybe-uninitialized]
#6 39.11  2468 |                     x_digits[0] |= 1;
#6 39.11       |                                 ^~
#6 39.36 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/dictobject.o Objects/dictobject.c
#6 39.43 In file included from Include/Python.h:110,
#6 39.43                  from Objects/dictobject.c:10:
#6 39.43 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 39.43    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 39.43       | ^~~~~~~~~~
#6 39.43 In file included from Include/Python.h:65,
#6 39.43                  from Objects/dictobject.c:10:
#6 39.43 Objects/dictobject.c: In function 'dictresize':
#6 39.43 Include/pymem.h:97:30: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#6 39.43    97 |  ( (type *) PyMem_MALLOC((n) * sizeof(type)) ) )
#6 39.43       |                              ^
#6 39.43 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#6 39.43    75 |     : malloc((n) ? (n) : 1))
#6 39.43       |               ^
#6 39.43 Objects/dictobject.c:651:20: note: in expansion of macro 'PyMem_NEW'
#6 39.43   651 |         newtable = PyMem_NEW(PyDictEntry, newsize);
#6 39.43       |                    ^~~~~~~~~
#6 40.35 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/memoryobject.o Objects/memoryobject.c
#6 40.42 In file included from Include/Python.h:110,
#6 40.42                  from Objects/memoryobject.c:4:
#6 40.42 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 40.42    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 40.42       | ^~~~~~~~~~
#6 40.70 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/methodobject.o Objects/methodobject.c
#6 40.76 In file included from Include/Python.h:110,
#6 40.76                  from Objects/methodobject.c:4:
#6 40.76 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 40.76    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 40.76       | ^~~~~~~~~~
#6 40.77 In file included from Include/Python.h:68,
#6 40.77                  from Objects/methodobject.c:4:
#6 40.77 Objects/methodobject.c: In function 'PyCFunction_NewEx':
#6 40.77 Include/objimpl.h:161:66: warning: right-hand operand of comma expression has no effect [-Wunused-value]
#6 40.77   161 |     ( Py_TYPE(op) = (typeobj), _Py_NewReference((PyObject *)(op)), (op) )
#6 40.77       |     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^~~~~~~~
#6 40.77 Objects/methodobject.c:23:9: note: in expansion of macro 'PyObject_INIT'
#6 40.77    23 |         PyObject_INIT(op, &PyCFunction_Type);
#6 40.77       |         ^~~~~~~~~~~~~
#6 40.87 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/moduleobject.o Objects/moduleobject.c
#6 40.93 In file included from Include/Python.h:110,
#6 40.93                  from Objects/moduleobject.c:4:
#6 40.93 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 40.93    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 40.93       | ^~~~~~~~~~
#6 41.09 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/object.o Objects/object.c
#6 41.16 In file included from Include/Python.h:110,
#6 41.16                  from Objects/object.c:4:
#6 41.16 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 41.16    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 41.16       | ^~~~~~~~~~
#6 41.65 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/obmalloc.o Objects/obmalloc.c
#6 41.71 In file included from Include/Python.h:110,
#6 41.71                  from Objects/obmalloc.c:1:
#6 41.71 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 41.71    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 41.71       | ^~~~~~~~~~
#6 41.81 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/capsule.o Objects/capsule.c
#6 41.87 In file included from Include/Python.h:110,
#6 41.87                  from Objects/capsule.c:3:
#6 41.87 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 41.87    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 41.87       | ^~~~~~~~~~
#6 41.97 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/rangeobject.o Objects/rangeobject.c
#6 42.04 In file included from Include/Python.h:110,
#6 42.04                  from Objects/rangeobject.c:3:
#6 42.04 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 42.04    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 42.04       | ^~~~~~~~~~
#6 42.38 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/setobject.o Objects/setobject.c
#6 42.44 In file included from Include/Python.h:110,
#6 42.44                  from Objects/setobject.c:10:
#6 42.44 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 42.44    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 42.44       | ^~~~~~~~~~
#6 42.45 Objects/setobject.c: In function 'set_insert_key':
#6 42.45 Objects/setobject.c:217:25: warning: typedef 'lookupfunc' locally defined but not used [-Wunused-local-typedefs]
#6 42.45   217 |     typedef setentry *(*lookupfunc)(PySetObject *, PyObject *, Py_hash_t);
#6 42.45       |                         ^~~~~~~~~~
#6 42.45 In file included from Include/Python.h:65,
#6 42.45                  from Objects/setobject.c:10:
#6 42.45 Objects/setobject.c: In function 'set_table_resize':
#6 42.45 Include/pymem.h:97:30: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#6 42.45    97 |  ( (type *) PyMem_MALLOC((n) * sizeof(type)) ) )
#6 42.45       |                              ^
#6 42.45 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#6 42.45    75 |     : malloc((n) ? (n) : 1))
#6 42.45       |               ^
#6 42.45 Objects/setobject.c:322:20: note: in expansion of macro 'PyMem_NEW'
#6 42.45   322 |         newtable = PyMem_NEW(setentry, newsize);
#6 42.45       |                    ^~~~~~~~~
#6 43.42 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/sliceobject.o Objects/sliceobject.c
#6 43.49 In file included from Include/Python.h:110,
#6 43.49                  from Objects/sliceobject.c:16:
#6 43.49 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 43.49    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 43.49       | ^~~~~~~~~~
#6 43.61 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/structseq.o Objects/structseq.c
#6 43.68 In file included from Include/Python.h:110,
#6 43.68                  from Objects/structseq.c:4:
#6 43.68 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 43.68    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 43.68       | ^~~~~~~~~~
#6 43.68 In file included from Include/Python.h:65,
#6 43.68                  from Objects/structseq.c:4:
#6 43.68 Objects/structseq.c: In function 'PyStructSequence_InitType':
#6 43.68 Include/pymem.h:97:30: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#6 43.68    97 |  ( (type *) PyMem_MALLOC((n) * sizeof(type)) ) )
#6 43.68       |                              ^
#6 43.68 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#6 43.68    75 |     : malloc((n) ? (n) : 1))
#6 43.68       |               ^
#6 43.68 Objects/structseq.c:344:15: note: in expansion of macro 'PyMem_NEW'
#6 43.68   344 |     members = PyMem_NEW(PyMemberDef, n_members-n_unnamed_members+1);
#6 43.68       |               ^~~~~~~~~
#6 43.73 Objects/structseq.c: In function 'structseq_repr':
#6 43.73 Objects/structseq.c:175:5: warning: 'strncpy' specified bound depends on the length of the source argument [-Wstringop-overflow=]
#6 43.73   175 |     strncpy(pbuf, typ->tp_name, len);
#6 43.73       |     ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#6 43.73 Objects/structseq.c:173:11: note: length computed here
#6 43.73   173 |     len = strlen(typ->tp_name) > TYPE_MAXSIZE ? TYPE_MAXSIZE :
#6 43.73       |           ^~~~~~~~~~~~~~~~~~~~
#6 43.84 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/tupleobject.o Objects/tupleobject.c
#6 43.91 In file included from Include/Python.h:110,
#6 43.91                  from Objects/tupleobject.c:4:
#6 43.91 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 43.91    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 43.91       | ^~~~~~~~~~
#6 44.27 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/typeobject.o Objects/typeobject.c
#6 44.34 In file included from Include/Python.h:110,
#6 44.34                  from Objects/typeobject.c:3:
#6 44.34 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 44.34    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 44.34       | ^~~~~~~~~~
#6 44.35 In file included from Include/Python.h:68,
#6 44.35                  from Objects/typeobject.c:3:
#6 44.35 Objects/typeobject.c: In function 'PyType_GenericAlloc':
#6 44.35 Include/objimpl.h:161:66: warning: right-hand operand of comma expression has no effect [-Wunused-value]
#6 44.35   161 |     ( Py_TYPE(op) = (typeobj), _Py_NewReference((PyObject *)(op)), (op) )
#6 44.35       |     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^~~~~~~~
#6 44.35 Objects/typeobject.c:721:9: note: in expansion of macro 'PyObject_INIT'
#6 44.35   721 |         PyObject_INIT(obj, type);
#6 44.35       |         ^~~~~~~~~~~~~
#6 44.35 In file included from Include/Python.h:65,
#6 44.35                  from Objects/typeobject.c:3:
#6 44.35 Objects/typeobject.c: In function 'pmerge':
#6 44.35 Objects/typeobject.c:1403:44: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#6 44.35  1403 |     remain = (int *)PyMem_MALLOC(SIZEOF_INT*to_merge_size);
#6 44.35 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#6 44.35    75 |     : malloc((n) ? (n) : 1))
#6 44.35       |               ^
#6 46.89 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/unicodeobject.o Objects/unicodeobject.c
#6 46.95 In file included from Include/Python.h:110,
#6 46.95                  from Objects/unicodeobject.c:43:
#6 46.95 Include/modsupport.h:27:1: warning: '_PyArg_ParseTuple_SizeT' is an unrecognized format function type [-Wformat=]
#6 46.95    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 46.95       | ^~~~~~~~~~
#6 46.96 In file included from Include/Python.h:68,
#6 46.96                  from Objects/unicodeobject.c:43:
#6 46.96 Objects/unicodeobject.c: In function '_PyUnicode_New':
#6 46.96 Include/objimpl.h:161:66: warning: right-hand operand of comma expression has no effect [-Wunused-value]
#6 46.96   161 |     ( Py_TYPE(op) = (typeobj), _Py_NewReference((PyObject *)(op)), (op) )
#6 46.96       |     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^~~~~~~~
#6 46.96 Objects/unicodeobject.c:361:9: note: in expansion of macro 'PyObject_INIT'
#6 46.96   361 |         PyObject_INIT(unicode, &PyUnicode_Type);
#6 46.96       |         ^~~~~~~~~~~~~
#6 46.96 In file included from Include/Python.h:65,
#6 46.96                  from Objects/unicodeobject.c:43:
#6 46.96 Objects/unicodeobject.c: In function 'PyUnicodeUCS2_AsWideCharString':
#6 46.96 Objects/unicodeobject.c:1335:34: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#6 46.96  1335 |     buffer = PyMem_MALLOC(buflen * sizeof(wchar_t));
#6 46.96 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#6 46.96    75 |     : malloc((n) ? (n) : 1))
#6 46.96       |               ^
#6 52.27 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/unicodectype.o Objects/unicodectype.c
#6 52.33 In file included from Include/Python.h:110,
#6 52.33                  from Objects/unicodectype.c:11:
#6 52.33 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 52.33    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 52.33       | ^~~~~~~~~~
#6 52.64 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/weakrefobject.o Objects/weakrefobject.c
#6 52.71 In file included from Include/Python.h:110,
#6 52.71                  from Objects/weakrefobject.c:1:
#6 52.71 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 52.71    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 52.71       | ^~~~~~~~~~
#6 53.27 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/_warnings.o Python/_warnings.c
#6 53.34 In file included from Include/Python.h:110,
#6 53.34                  from Python/_warnings.c:1:
#6 53.34 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 53.34    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 53.34       | ^~~~~~~~~~
#6 53.64 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/Python-ast.o Python/Python-ast.c
#6 53.71 In file included from Include/Python.h:110,
#6 53.71                  from Python/Python-ast.c:12:
#6 53.71 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 53.71    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 53.71       | ^~~~~~~~~~
#6 56.65 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/asdl.o Python/asdl.c
#6 56.72 In file included from Include/Python.h:110,
#6 56.72                  from Python/asdl.c:1:
#6 56.72 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 56.72    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 56.72       | ^~~~~~~~~~
#6 56.75 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/dynamic_annotations.o Python/dynamic_annotations.c
#6 56.77 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/mysnprintf.o Python/mysnprintf.c
#6 56.84 In file included from Include/Python.h:110,
#6 56.84                  from Python/mysnprintf.c:1:
#6 56.84 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 56.84    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 56.84       | ^~~~~~~~~~
#6 56.87 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/pyctype.o Python/pyctype.c
#6 56.93 In file included from Include/Python.h:110,
#6 56.93                  from Python/pyctype.c:1:
#6 56.93 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 56.93    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 56.93       | ^~~~~~~~~~
#6 56.95 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/tokenizer_pgen.o Parser/tokenizer_pgen.c
#6 57.01 In file included from Include/Python.h:110,
#6 57.01                  from Parser/tokenizer.c:4,
#6 57.01                  from Parser/tokenizer_pgen.c:2:
#6 57.01 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 57.01    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 57.01       | ^~~~~~~~~~
#6 57.32 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/printgrammar.o Parser/printgrammar.c
#6 57.38 In file included from Include/Python.h:110,
#6 57.38                  from Include/pgenheaders.h:10,
#6 57.38                  from Parser/printgrammar.c:6:
#6 57.38 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 57.38    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 57.38       | ^~~~~~~~~~
#6 57.44 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/pgenmain.o Parser/pgenmain.c
#6 57.51 In file included from Include/Python.h:110,
#6 57.51                  from Parser/pgenmain.c:18:
#6 57.51 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 57.51    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 57.51       | ^~~~~~~~~~
#6 57.57 gcc -pthread -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes    Parser/acceler.o Parser/grammar1.o Parser/listnode.o Parser/node.o Parser/parser.o Parser/parsetok.o Parser/bitset.o Parser/metagrammar.o Parser/firstsets.o Parser/grammar.o Parser/pgen.o Objects/obmalloc.o Python/dynamic_annotations.o Python/mysnprintf.o Python/pyctype.o Parser/tokenizer_pgen.o Parser/printgrammar.o Parser/pgenmain.o -lpthread -ldl  -lutil -o Parser/pgen
#6 57.60 Parser/pgen ./Grammar/Grammar Include/graminit.h Python/graminit.c
#6 57.61 touch Parser/pgen.stamp
#6 57.61 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/ast.o Python/ast.c
#6 57.67 In file included from Include/Python.h:110,
#6 57.67                  from Python/ast.c:6:
#6 57.67 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 57.67    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 57.67       | ^~~~~~~~~~
#6 58.86 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/bltinmodule.o Python/bltinmodule.c
#6 58.92 In file included from Include/Python.h:110,
#6 58.92                  from Python/bltinmodule.c:3:
#6 58.92 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 58.92    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 58.92       | ^~~~~~~~~~
#6 59.56 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/ceval.o Python/ceval.c
#6 59.63 In file included from Include/Python.h:110,
#6 59.63                  from Python/ceval.c:12:
#6 59.63 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 59.63    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 59.63       | ^~~~~~~~~~
#6 62.96 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/compile.o Python/compile.c
#6 63.03 In file included from Include/Python.h:110,
#6 63.03                  from Python/compile.c:24:
#6 63.03 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 63.03    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 63.03       | ^~~~~~~~~~
#6 63.64 In function 'assemble_lnotab',
#6 63.64     inlined from 'assemble_emit' at Python/compile.c:3802:25,
#6 63.64     inlined from 'assemble' at Python/compile.c:4095:18:
#6 63.64 Python/compile.c:3753:19: warning: writing 1 byte into a region of size 0 [-Wstringop-overflow=]
#6 63.64  3753 |         *lnotab++ = 255;
#6 63.64       |         ~~~~~~~~~~^~~~~
#6 64.71 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/codecs.o Python/codecs.c
#6 64.77 In file included from Include/Python.h:110,
#6 64.77                  from Python/codecs.c:11:
#6 64.77 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 64.77    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 64.77       | ^~~~~~~~~~
#6 65.15 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/errors.o Python/errors.c
#6 65.22 In file included from Include/Python.h:110,
#6 65.22                  from Python/errors.c:4:
#6 65.22 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 65.22    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 65.22       | ^~~~~~~~~~
#6 65.59 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/frozen.o Python/frozen.c
#6 65.65 In file included from Include/Python.h:110,
#6 65.65                  from Python/frozen.c:4:
#6 65.65 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 65.65    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 65.65       | ^~~~~~~~~~
#6 65.67 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/frozenmain.o Python/frozenmain.c
#6 65.73 In file included from Include/Python.h:110,
#6 65.73                  from Python/frozenmain.c:4:
#6 65.73 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 65.73    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 65.73       | ^~~~~~~~~~
#6 65.78 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/future.o Python/future.c
#6 65.85 In file included from Include/Python.h:110,
#6 65.85                  from Python/future.c:1:
#6 65.85 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 65.85    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 65.85       | ^~~~~~~~~~
#6 65.91 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/getargs.o Python/getargs.c
#6 65.97 In file included from Include/Python.h:110,
#6 65.97                  from Python/getargs.c:4:
#6 65.97 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 65.97    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 65.97       | ^~~~~~~~~~
#6 65.99 In file included from Include/Python.h:65,
#6 65.99                  from Python/getargs.c:4:
#6 65.99 Python/getargs.c: In function 'convertsimple':
#6 65.99 Include/pymem.h:97:30: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#6 65.99    97 |  ( (type *) PyMem_MALLOC((n) * sizeof(type)) ) )
#6 65.99       |                              ^
#6 65.99 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#6 65.99    75 |     : malloc((n) ? (n) : 1))
#6 65.99       |               ^
#6 65.99 Python/getargs.c:1107:27: note: in expansion of macro 'PyMem_NEW'
#6 65.99  1107 |                 *buffer = PyMem_NEW(char, size + 1);
#6 65.99       |                           ^~~~~~~~~
#6 65.99 Include/pymem.h:97:30: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#6 65.99    97 |  ( (type *) PyMem_MALLOC((n) * sizeof(type)) ) )
#6 65.99       |                              ^
#6 65.99 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#6 65.99    75 |     : malloc((n) ? (n) : 1))
#6 65.99       |               ^
#6 65.99 Python/getargs.c:1149:23: note: in expansion of macro 'PyMem_NEW'
#6 65.99  1149 |             *buffer = PyMem_NEW(char, size + 1);
#6 65.99       |                       ^~~~~~~~~
#6 66.73 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/getcompiler.o Python/getcompiler.c
#6 66.79 In file included from Include/Python.h:110,
#6 66.79                  from Python/getcompiler.c:4:
#6 66.79 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 66.79    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 66.79       | ^~~~~~~~~~
#6 66.81 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/getcopyright.o Python/getcopyright.c
#6 66.88 In file included from Include/Python.h:110,
#6 66.88                  from Python/getcopyright.c:3:
#6 66.88 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 66.88    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 66.88       | ^~~~~~~~~~
#6 66.89 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -DPLATFORM='"linux2"' -o Python/getplatform.o ./Python/getplatform.c
#6 66.96 In file included from Include/Python.h:110,
#6 66.96                  from ./Python/getplatform.c:2:
#6 66.96 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 66.96    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 66.96       | ^~~~~~~~~~
#6 66.98 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/getversion.o Python/getversion.c
#6 67.05 In file included from Include/Python.h:110,
#6 67.05                  from Python/getversion.c:4:
#6 67.05 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 67.05    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 67.05       | ^~~~~~~~~~
#6 67.07 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/graminit.o Python/graminit.c
#6 67.14 In file included from Include/Python.h:110,
#6 67.14                  from Include/pgenheaders.h:10,
#6 67.14                  from Python/graminit.c:3:
#6 67.14 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 67.14    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 67.14       | ^~~~~~~~~~
#6 67.17 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/import.o Python/import.c
#6 67.23 In file included from Include/Python.h:110,
#6 67.23                  from Python/import.c:4:
#6 67.23 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 67.23    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 67.23       | ^~~~~~~~~~
#6 67.24 In file included from Include/Python.h:65,
#6 67.24                  from Python/import.c:4:
#6 67.24 Python/import.c: In function '_PyImport_Init':
#6 67.24 Include/pymem.h:97:30: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#6 67.24    97 |  ( (type *) PyMem_MALLOC((n) * sizeof(type)) ) )
#6 67.24       |                              ^
#6 67.24 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#6 67.24    75 |     : malloc((n) ? (n) : 1))
#6 67.24       |               ^
#6 67.24 Python/import.c:163:15: note: in expansion of macro 'PyMem_NEW'
#6 67.24   163 |     filetab = PyMem_NEW(struct filedescr, countD + countS + 1);
#6 67.24       |               ^~~~~~~~~
#6 67.29 Python/import.c: In function 'PyImport_ExtendInittab':
#6 67.29 Include/pymem.h:110:34: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#6 67.29   110 |  (type *) PyMem_REALLOC((p), (n) * sizeof(type)) )
#6 67.29       |                                  ^
#6 67.29 Include/pymem.h:77:21: note: in definition of macro 'PyMem_REALLOC'
#6 67.29    77 |     : realloc((p), (n) ? (n) : 1))
#6 67.29       |                     ^
#6 67.29 Python/import.c:3984:5: note: in expansion of macro 'PyMem_RESIZE'
#6 67.29  3984 |     PyMem_RESIZE(p, struct _inittab, i+n+1);
#6 67.29       |     ^~~~~~~~~~~~
#6 68.28 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -I. -o Python/importdl.o ./Python/importdl.c
#6 68.34 In file included from Include/Python.h:110,
#6 68.34                  from ./Python/importdl.c:4:
#6 68.34 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 68.34    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 68.34       | ^~~~~~~~~~
#6 68.38 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/marshal.o Python/marshal.c
#6 68.45 In file included from Include/Python.h:110,
#6 68.45                  from Python/marshal.c:9:
#6 68.45 Include/modsupport.h:27:1: warning: '_PyArg_ParseTuple_SizeT' is an unrecognized format function type [-Wformat=]
#6 68.45    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 68.45       | ^~~~~~~~~~
#6 68.46 In file included from Include/Python.h:65,
#6 68.46                  from Python/marshal.c:9:
#6 68.46 Python/marshal.c: In function 'r_object':
#6 68.46 Include/pymem.h:97:30: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#6 68.46    97 |  ( (type *) PyMem_MALLOC((n) * sizeof(type)) ) )
#6 68.46       |                              ^
#6 68.46 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#6 68.46    75 |     : malloc((n) ? (n) : 1))
#6 68.46       |               ^
#6 68.46 Python/marshal.c:877:18: note: in expansion of macro 'PyMem_NEW'
#6 68.46   877 |         buffer = PyMem_NEW(char, n);
#6 68.46       |                  ^~~~~~~~~
#6 68.92 Python/marshal.c: In function 'PyMarshal_WriteLongToFile':
#6 68.92 Python/marshal.c:69:35: warning: 'wf.ptr' may be used uninitialized in this function [-Wmaybe-uninitialized]
#6 68.92    69 |                       else if ((p)->ptr != (p)->end) *(p)->ptr++ = (c); \
#6 68.92       |                                   ^~
#6 68.92 Python/marshal.c:69:47: warning: 'wf.end' may be used uninitialized in this function [-Wmaybe-uninitialized]
#6 68.92    69 |                       else if ((p)->ptr != (p)->end) *(p)->ptr++ = (c); \
#6 68.92       |                                               ^~
#6 68.92 Python/marshal.c:76:10: warning: 'wf.str' may be used uninitialized in this function [-Wmaybe-uninitialized]
#6 68.92    76 |     if (p->str == NULL)
#6 68.92       |         ~^~~~~
#6 69.04 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/modsupport.o Python/modsupport.c
#6 69.10 In file included from Include/Python.h:110,
#6 69.10                  from Python/modsupport.c:4:
#6 69.10 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 69.10    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 69.10       | ^~~~~~~~~~
#6 69.34 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/mystrtoul.o Python/mystrtoul.c
#6 69.40 In file included from Include/Python.h:110,
#6 69.40                  from Python/mystrtoul.c:2:
#6 69.40 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 69.40    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 69.40       | ^~~~~~~~~~
#6 69.48 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/peephole.o Python/peephole.c
#6 69.55 In file included from Include/Python.h:110,
#6 69.55                  from Python/peephole.c:3:
#6 69.55 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 69.55    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 69.55       | ^~~~~~~~~~
#6 69.82 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/pyarena.o Python/pyarena.c
#6 69.88 In file included from Include/Python.h:110,
#6 69.88                  from Python/pyarena.c:1:
#6 69.88 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 69.88    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 69.88       | ^~~~~~~~~~
#6 69.89 Python/pyarena.c: In function 'PyArena_Free':
#6 69.89 Python/pyarena.c:161:9: warning: variable 'r' set but not used [-Wunused-but-set-variable]
#6 69.89   161 |     int r;
#6 69.89       |         ^
#6 69.94 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/pyfpe.o Python/pyfpe.c
#6 69.96 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/pymath.o Python/pymath.c
#6 70.03 In file included from Include/Python.h:110,
#6 70.03                  from Python/pymath.c:1:
#6 70.03 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 70.03    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 70.03       | ^~~~~~~~~~
#6 70.05 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/pystate.o Python/pystate.c
#6 70.11 In file included from Include/Python.h:110,
#6 70.11                  from Python/pystate.c:4:
#6 70.11 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 70.11    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 70.11       | ^~~~~~~~~~
#6 70.31 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/pythonrun.o Python/pythonrun.c
#6 70.38 In file included from Include/Python.h:110,
#6 70.38                  from Python/pythonrun.c:4:
#6 70.38 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 70.38    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 70.38       | ^~~~~~~~~~
#6 71.13 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/pytime.o Python/pytime.c
#6 71.19 In file included from Include/Python.h:110,
#6 71.19                  from Python/pytime.c:1:
#6 71.19 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 71.19    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 71.19       | ^~~~~~~~~~
#6 71.20 Python/pytime.c: In function '_PyTime_gettimeofday':
#6 71.20 Python/pytime.c:45:9: warning: 'ftime' is deprecated [-Wdeprecated-declarations]
#6 71.20    45 |         ftime(&t);
#6 71.20       |         ^~~~~
#6 71.20 In file included from Python/pytime.c:16:
#6 71.20 /usr/include/x86_64-linux-gnu/sys/timeb.h:39:12: note: declared here
#6 71.20    39 | extern int ftime (struct timeb *__timebuf)
#6 71.20       |            ^~~~~
#6 71.22 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/random.o Python/random.c
#6 71.28 In file included from Include/Python.h:110,
#6 71.28                  from Python/random.c:1:
#6 71.28 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 71.28    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 71.28       | ^~~~~~~~~~
#6 71.35 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/structmember.o Python/structmember.c
#6 71.41 In file included from Include/Python.h:110,
#6 71.41                  from Python/structmember.c:4:
#6 71.41 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 71.41    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 71.41       | ^~~~~~~~~~
#6 71.50 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/symtable.o Python/symtable.c
#6 71.57 In file included from Include/Python.h:110,
#6 71.57                  from Python/symtable.c:1:
#6 71.57 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 71.57    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 71.57       | ^~~~~~~~~~
#6 72.26 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE \
#6 72.26 	-DABIFLAGS='"m"' \
#6 72.26 	-o Python/sysmodule.o ./Python/sysmodule.c
#6 72.32 In file included from Include/Python.h:110,
#6 72.32                  from ./Python/sysmodule.c:17:
#6 72.32 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 72.32    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 72.32       | ^~~~~~~~~~
#6 72.34 ./Python/sysmodule.c: In function 'PySys_AddXOption':
#6 72.34 ./Python/sysmodule.c:1180:9: warning: variable 'r' set but not used [-Wunused-but-set-variable]
#6 72.34  1180 |     int r;
#6 72.34       |         ^
#6 72.78 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/traceback.o Python/traceback.c
#6 72.84 In file included from Include/Python.h:110,
#6 72.84                  from Python/traceback.c:4:
#6 72.84 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 72.84    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 72.84       | ^~~~~~~~~~
#6 73.00 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/getopt.o Python/getopt.c
#6 73.07 In file included from Include/Python.h:110,
#6 73.07                  from Python/getopt.c:30:
#6 73.07 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 73.07    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 73.07       | ^~~~~~~~~~
#6 73.11 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/pystrcmp.o Python/pystrcmp.c
#6 73.17 In file included from Include/Python.h:110,
#6 73.17                  from Python/pystrcmp.c:4:
#6 73.17 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 73.17    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 73.17       | ^~~~~~~~~~
#6 73.22 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/pystrtod.o Python/pystrtod.c
#6 73.28 In file included from Include/Python.h:110,
#6 73.28                  from Python/pystrtod.c:3:
#6 73.28 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 73.28    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 73.28       | ^~~~~~~~~~
#6 73.40 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/dtoa.o Python/dtoa.c
#6 73.46 In file included from Include/Python.h:110,
#6 73.46                  from Python/dtoa.c:117:
#6 73.46 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 73.46    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 73.46       | ^~~~~~~~~~
#6 74.60 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/formatter_unicode.o Python/formatter_unicode.c
#6 74.66 In file included from Include/Python.h:110,
#6 74.66                  from Python/formatter_unicode.c:5:
#6 74.66 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 74.66    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 74.66       | ^~~~~~~~~~
#6 75.10 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/fileutils.o Python/fileutils.c
#6 75.17 In file included from Include/Python.h:110,
#6 75.17                  from Python/fileutils.c:1:
#6 75.17 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 75.17    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 75.17       | ^~~~~~~~~~
#6 75.33 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE \
#6 75.33 	-DSOABI='"cpython-32m"' \
#6 75.33 	-o Python/dynload_shlib.o ./Python/dynload_shlib.c
#6 75.39 In file included from Include/Python.h:110,
#6 75.39                  from ./Python/dynload_shlib.c:4:
#6 75.39 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 75.39    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 75.39       | ^~~~~~~~~~
#6 75.44 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/thread.o Python/thread.c
#6 75.50 In file included from Include/Python.h:110,
#6 75.50                  from Python/thread.c:8:
#6 75.50 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 75.50    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 75.50       | ^~~~~~~~~~
#6 75.59 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Modules/config.o Modules/config.c
#6 75.66 In file included from Include/Python.h:110,
#6 75.66                  from Modules/config.c:19:
#6 75.66 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 75.66    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 75.66       | ^~~~~~~~~~
#6 75.67 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -DPYTHONPATH='":plat-linux2"' \
#6 75.67 	-DPREFIX='"/usr/local"' \
#6 75.67 	-DEXEC_PREFIX='"/usr/local"' \
#6 75.67 	-DVERSION='"3.2"' \
#6 75.67 	-DVPATH='""' \
#6 75.67 	-o Modules/getpath.o ./Modules/getpath.c
#6 75.74 In file included from Include/Python.h:110,
#6 75.74                  from ./Modules/getpath.c:3:
#6 75.74 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 75.74    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 75.74       | ^~~~~~~~~~
#6 75.95 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Modules/main.o Modules/main.c
#6 76.01 In file included from Include/Python.h:110,
#6 76.01                  from Modules/main.c:3:
#6 76.01 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 76.01    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 76.01       | ^~~~~~~~~~
#6 76.20 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Modules/gcmodule.o Modules/gcmodule.c
#6 76.26 In file included from Include/Python.h:110,
#6 76.26                  from Modules/gcmodule.c:26:
#6 76.26 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 76.26    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 76.26       | ^~~~~~~~~~
#6 76.62 gcc -pthread  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/_threadmodule.c -o Modules/_threadmodule.o
#6 76.68 In file included from Include/Python.h:110,
#6 76.68                  from ./Modules/_threadmodule.c:5:
#6 76.68 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 76.68    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 76.68       | ^~~~~~~~~~
#6 76.94 gcc -pthread  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/signalmodule.c -o Modules/signalmodule.o
#6 77.01 In file included from Include/Python.h:110,
#6 77.01                  from ./Modules/signalmodule.c:6:
#6 77.01 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 77.01    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 77.01       | ^~~~~~~~~~
#6 77.24 gcc -pthread  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/posixmodule.c -o Modules/posixmodule.o
#6 77.31 In file included from Include/Python.h:110,
#6 77.31                  from ./Modules/posixmodule.c:28:
#6 77.31 Include/modsupport.h:27:1: warning: '_PyArg_ParseTuple_SizeT' is an unrecognized format function type [-Wformat=]
#6 77.31    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 77.31       | ^~~~~~~~~~
#6 77.34 In file included from Include/Python.h:65,
#6 77.34                  from ./Modules/posixmodule.c:28:
#6 77.34 ./Modules/posixmodule.c: In function 'posix_execv':
#6 77.34 Include/pymem.h:97:30: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#6 77.34    97 |  ( (type *) PyMem_MALLOC((n) * sizeof(type)) ) )
#6 77.34       |                              ^
#6 77.34 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#6 77.34    75 |     : malloc((n) ? (n) : 1))
#6 77.34       |               ^
#6 77.34 ./Modules/posixmodule.c:3667:16: note: in expansion of macro 'PyMem_NEW'
#6 77.34  3667 |     argvlist = PyMem_NEW(char *, argc+1);
#6 77.34       |                ^~~~~~~~~
#6 77.34 ./Modules/posixmodule.c: In function 'parse_envlist':
#6 77.34 Include/pymem.h:97:30: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#6 77.34    97 |  ( (type *) PyMem_MALLOC((n) * sizeof(type)) ) )
#6 77.34       |                              ^
#6 77.34 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#6 77.34    75 |     : malloc((n) ? (n) : 1))
#6 77.34       |               ^
#6 77.34 ./Modules/posixmodule.c:3707:15: note: in expansion of macro 'PyMem_NEW'
#6 77.34  3707 |     envlist = PyMem_NEW(char *, i + 1);
#6 77.34       |               ^~~~~~~~~
#6 77.34 Include/pymem.h:97:30: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#6 77.34    97 |  ( (type *) PyMem_MALLOC((n) * sizeof(type)) ) )
#6 77.34       |                              ^
#6 77.34 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#6 77.34    75 |     : malloc((n) ? (n) : 1))
#6 77.34       |               ^
#6 77.34 ./Modules/posixmodule.c:3744:13: note: in expansion of macro 'PyMem_NEW'
#6 77.34  3744 |         p = PyMem_NEW(char, len);
#6 77.34       |             ^~~~~~~~~
#6 77.34 ./Modules/posixmodule.c: In function 'posix_execve':
#6 77.34 Include/pymem.h:97:30: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#6 77.34    97 |  ( (type *) PyMem_MALLOC((n) * sizeof(type)) ) )
#6 77.34       |                              ^
#6 77.34 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#6 77.34    75 |     : malloc((n) ? (n) : 1))
#6 77.34       |               ^
#6 77.34 ./Modules/posixmodule.c:3823:16: note: in expansion of macro 'PyMem_NEW'
#6 77.34  3823 |     argvlist = PyMem_NEW(char *, argc+1);
#6 77.34       |                ^~~~~~~~~
#6 78.41 gcc -pthread  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/errnomodule.c -o Modules/errnomodule.o
#6 78.48 In file included from Include/Python.h:110,
#6 78.48                  from ./Modules/errnomodule.c:4:
#6 78.48 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 78.48    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 78.48       | ^~~~~~~~~~
#6 78.55 gcc -pthread  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/pwdmodule.c -o Modules/pwdmodule.o
#6 78.61 In file included from Include/Python.h:110,
#6 78.61                  from ./Modules/pwdmodule.c:4:
#6 78.61 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 78.61    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 78.61       | ^~~~~~~~~~
#6 78.68 gcc -pthread  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/_sre.c -o Modules/_sre.o
#6 78.75 In file included from Include/Python.h:110,
#6 78.75                  from ./Modules/_sre.c:44:
#6 78.75 Include/modsupport.h:27:1: warning: '_PyArg_ParseTuple_SizeT' is an unrecognized format function type [-Wformat=]
#6 78.75    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 78.75       | ^~~~~~~~~~
#6 78.79 ./Modules/_sre.c: In function '_validate_inner':
#6 78.79 ./Modules/_sre.c:3014:42: warning: variable 'prefix_skip' set but not used [-Wunused-but-set-variable]
#6 78.79  3014 |                     SRE_CODE prefix_len, prefix_skip;
#6 78.79       |                                          ^~~~~~~~~~~
#6 78.79 ./Modules/_sre.c:2992:38: warning: variable 'max' set but not used [-Wunused-but-set-variable]
#6 78.79  2992 |                 SRE_CODE flags, min, max, i;
#6 78.79       |                                      ^~~
#6 78.79 ./Modules/_sre.c:2992:33: warning: variable 'min' set but not used [-Wunused-but-set-variable]
#6 78.79  2992 |                 SRE_CODE flags, min, max, i;
#6 78.79       |                                 ^~~
#6 81.58 gcc -pthread  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/_codecsmodule.c -o Modules/_codecsmodule.o
#6 81.65 In file included from Include/Python.h:110,
#6 81.65                  from ./Modules/_codecsmodule.c:39:
#6 81.65 Include/modsupport.h:27:1: warning: '_PyArg_ParseTuple_SizeT' is an unrecognized format function type [-Wformat=]
#6 81.65    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 81.65       | ^~~~~~~~~~
#6 81.98 gcc -pthread  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/_weakref.c -o Modules/_weakref.o
#6 82.05 In file included from Include/Python.h:110,
#6 82.05                  from ./Modules/_weakref.c:1:
#6 82.05 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 82.05    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 82.05       | ^~~~~~~~~~
#6 82.09 gcc -pthread  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/_functoolsmodule.c -o Modules/_functoolsmodule.o
#6 82.16 In file included from Include/Python.h:110,
#6 82.16                  from ./Modules/_functoolsmodule.c:2:
#6 82.16 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 82.16    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 82.16       | ^~~~~~~~~~
#6 82.29 gcc -pthread  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/operator.c -o Modules/operator.o
#6 82.36 In file included from Include/Python.h:110,
#6 82.36                  from ./Modules/operator.c:2:
#6 82.36 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 82.36    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 82.36       | ^~~~~~~~~~
#6 82.66 gcc -pthread  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/_collectionsmodule.c -o Modules/_collectionsmodule.o
#6 82.72 In file included from Include/Python.h:110,
#6 82.72                  from ./Modules/_collectionsmodule.c:1:
#6 82.72 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 82.72    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 82.72       | ^~~~~~~~~~
#6 82.73 ./Modules/_collectionsmodule.c: In function 'deque_clearmethod':
#6 82.73 ./Modules/_collectionsmodule.c:707:9: warning: variable 'rv' set but not used [-Wunused-but-set-variable]
#6 82.73   707 |     int rv;
#6 82.73       |         ^~
#6 83.27 gcc -pthread  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/itertoolsmodule.c -o Modules/itertoolsmodule.o
#6 83.33 In file included from Include/Python.h:110,
#6 83.33                  from ./Modules/itertoolsmodule.c:2:
#6 83.33 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 83.33    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 83.33       | ^~~~~~~~~~
#6 84.19 gcc -pthread  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/_localemodule.c -o Modules/_localemodule.o
#6 84.26 In file included from Include/Python.h:110,
#6 84.26                  from ./Modules/_localemodule.c:13:
#6 84.26 Include/modsupport.h:27:1: warning: '_PyArg_ParseTuple_SizeT' is an unrecognized format function type [-Wformat=]
#6 84.26    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 84.26       | ^~~~~~~~~~
#6 84.43 gcc -pthread  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -I./Modules/_io -c ./Modules/_io/_iomodule.c -o Modules/_iomodule.o
#6 84.50 In file included from Include/Python.h:110,
#6 84.50                  from ./Modules/_io/_iomodule.c:11:
#6 84.50 Include/modsupport.h:27:1: warning: '_PyArg_ParseTuple_SizeT' is an unrecognized format function type [-Wformat=]
#6 84.50    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 84.50       | ^~~~~~~~~~
#6 84.71 gcc -pthread  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -I./Modules/_io -c ./Modules/_io/iobase.c -o Modules/iobase.o
#6 84.78 In file included from Include/Python.h:110,
#6 84.78                  from ./Modules/_io/iobase.c:12:
#6 84.78 Include/modsupport.h:27:1: warning: '_PyArg_ParseTuple_SizeT' is an unrecognized format function type [-Wformat=]
#6 84.78    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 84.78       | ^~~~~~~~~~
#6 85.01 gcc -pthread  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -I./Modules/_io -c ./Modules/_io/fileio.c -o Modules/fileio.o
#6 85.08 In file included from Include/Python.h:110,
#6 85.08                  from ./Modules/_io/fileio.c:4:
#6 85.08 Include/modsupport.h:27:1: warning: '_PyArg_ParseTuple_SizeT' is an unrecognized format function type [-Wformat=]
#6 85.08    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 85.08       | ^~~~~~~~~~
#6 85.35 gcc -pthread  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -I./Modules/_io -c ./Modules/_io/bytesio.c -o Modules/bytesio.o
#6 85.41 In file included from Include/Python.h:110,
#6 85.41                  from ./Modules/_io/bytesio.c:1:
#6 85.41 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 85.41    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 85.41       | ^~~~~~~~~~
#6 85.42 ./Modules/_io/bytesio.c: In function 'bytesiobuf_getbuffer':
#6 85.42 ./Modules/_io/bytesio.c:965:11: warning: variable 'ptr' set but not used [-Wunused-but-set-variable]
#6 85.42   965 |     void *ptr;
#6 85.42       |           ^~~
#6 85.70 gcc -pthread  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -I./Modules/_io -c ./Modules/_io/bufferedio.c -o Modules/bufferedio.o
#6 85.76 In file included from Include/Python.h:110,
#6 85.76                  from ./Modules/_io/bufferedio.c:11:
#6 85.76 Include/modsupport.h:27:1: warning: '_PyArg_ParseTuple_SizeT' is an unrecognized format function type [-Wformat=]
#6 85.76    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 85.76       | ^~~~~~~~~~
#6 86.50 gcc -pthread  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -I./Modules/_io -c ./Modules/_io/textio.c -o Modules/textio.o
#6 86.58 In file included from Include/Python.h:110,
#6 86.58                  from ./Modules/_io/textio.c:10:
#6 86.58 Include/modsupport.h:27:1: warning: '_PyArg_ParseTuple_SizeT' is an unrecognized format function type [-Wformat=]
#6 86.58    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 86.58       | ^~~~~~~~~~
#6 87.43 gcc -pthread  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -I./Modules/_io -c ./Modules/_io/stringio.c -o Modules/stringio.o
#6 87.50 In file included from Include/Python.h:110,
#6 87.50                  from ./Modules/_io/stringio.c:2:
#6 87.50 Include/modsupport.h:27:1: warning: '_PyArg_ParseTuple_SizeT' is an unrecognized format function type [-Wformat=]
#6 87.50    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 87.50       | ^~~~~~~~~~
#6 87.75 gcc -pthread  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/zipimport.c -o Modules/zipimport.o
#6 87.82 In file included from Include/Python.h:110,
#6 87.82                  from ./Modules/zipimport.c:1:
#6 87.82 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 87.82    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 87.82       | ^~~~~~~~~~
#6 88.16 gcc -pthread  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/symtablemodule.c -o Modules/symtablemodule.o
#6 88.23 In file included from Include/Python.h:110,
#6 88.23                  from ./Modules/symtablemodule.c:1:
#6 88.23 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 88.23    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 88.23       | ^~~~~~~~~~
#6 88.27 gcc -pthread  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/xxsubtype.c -o Modules/xxsubtype.o
#6 88.34 In file included from Include/Python.h:110,
#6 88.34                  from ./Modules/xxsubtype.c:1:
#6 88.34 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 88.34    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 88.34       | ^~~~~~~~~~
#6 88.40 gcc -pthread -c  -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE \
#6 88.40       -DSVNVERSION="\"`LC_ALL=C echo Unversioned directory`\"" \
#6 88.40       -DHGVERSION="\"`LC_ALL=C `\"" \
#6 88.40       -DHGTAG="\"`LC_ALL=C `\"" \
#6 88.40       -DHGBRANCH="\"`LC_ALL=C `\"" \
#6 88.40       -o Modules/getbuildinfo.o ./Modules/getbuildinfo.c
#6 88.47 In file included from Include/Python.h:110,
#6 88.47                  from ./Modules/getbuildinfo.c:1:
#6 88.47 Include/modsupport.h:27:1: warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]
#6 88.47    27 | PyAPI_FUNC(int) PyArg_ParseTuple(PyObject *, const char *, ...) Py_FORMAT_PARSETUPLE(PyArg_ParseTuple, 2, 3);
#6 88.47       | ^~~~~~~~~~
#6 88.49 rm -f libpython3.2m.a
#6 88.49 ar rc libpython3.2m.a Modules/getbuildinfo.o
#6 88.50 ar rc libpython3.2m.a Parser/acceler.o Parser/grammar1.o Parser/listnode.o Parser/node.o Parser/parser.o Parser/parsetok.o Parser/bitset.o Parser/metagrammar.o Parser/firstsets.o Parser/grammar.o Parser/pgen.o Parser/myreadline.o Parser/tokenizer.o
#6 88.50 ar rc libpython3.2m.a Objects/abstract.o Objects/accu.o Objects/boolobject.o Objects/bytes_methods.o Objects/bytearrayobject.o Objects/bytesobject.o Objects/cellobject.o Objects/classobject.o Objects/codeobject.o Objects/complexobject.o Objects/descrobject.o Objects/enumobject.o Objects/exceptions.o Objects/genobject.o Objects/fileobject.o Objects/floatobject.o Objects/frameobject.o Objects/funcobject.o Objects/iterobject.o Objects/listobject.o Objects/longobject.o Objects/dictobject.o Objects/memoryobject.o Objects/methodobject.o Objects/moduleobject.o Objects/object.o Objects/obmalloc.o Objects/capsule.o Objects/rangeobject.o Objects/setobject.o Objects/sliceobject.o Objects/structseq.o Objects/tupleobject.o Objects/typeobject.o Objects/unicodeobject.o Objects/unicodectype.o Objects/weakrefobject.o
#6 88.53 ar rc libpython3.2m.a Python/_warnings.o Python/Python-ast.o Python/asdl.o Python/ast.o Python/bltinmodule.o Python/ceval.o Python/compile.o Python/codecs.o Python/dynamic_annotations.o Python/errors.o Python/frozen.o Python/frozenmain.o Python/future.o Python/getargs.o Python/getcompiler.o Python/getcopyright.o Python/getplatform.o Python/getversion.o Python/graminit.o Python/import.o Python/importdl.o Python/marshal.o Python/modsupport.o Python/mystrtoul.o Python/mysnprintf.o Python/peephole.o Python/pyarena.o Python/pyctype.o Python/pyfpe.o Python/pymath.o Python/pystate.o Python/pythonrun.o Python/pytime.o Python/random.o Python/structmember.o Python/symtable.o Python/sysmodule.o Python/traceback.o Python/getopt.o Python/pystrcmp.o Python/pystrtod.o Python/dtoa.o Python/formatter_unicode.o Python/fileutils.o Python/dynload_shlib.o   Python/thread.o
#6 88.58 ar rc libpython3.2m.a Modules/config.o Modules/getpath.o Modules/main.o Modules/gcmodule.o
#6 88.63 ar rc libpython3.2m.a Modules/_threadmodule.o  Modules/signalmodule.o  Modules/posixmodule.o  Modules/errnomodule.o  Modules/pwdmodule.o  Modules/_sre.o  Modules/_codecsmodule.o  Modules/_weakref.o  Modules/_functoolsmodule.o  Modules/operator.o  Modules/_collectionsmodule.o  Modules/itertoolsmodule.o  Modules/_localemodule.o  Modules/_iomodule.o Modules/iobase.o Modules/fileio.o Modules/bytesio.o Modules/bufferedio.o Modules/textio.o Modules/stringio.o  Modules/zipimport.o  Modules/symtablemodule.o  Modules/xxsubtype.o
#6 88.69 ranlib libpython3.2m.a
#6 88.75 gcc -pthread   -Xlinker -export-dynamic -o python Modules/python.o libpython3.2m.a -lpthread -ldl  -lutil   -lm
#6 88.93 Segmentation fault
#6 88.93 make: *** [Makefile:467: sharedmods] Error 139
------
executor failed running [/bin/sh -c curl -SL https://www.python.org/ftp/python/3.2.6/Python-3.2.6.tgz | tar -xzvf -     && cd Python-3.2.6 && ./configure && make && make altinstall]: exit code: 2
</pre>

</details>


<details>
<summary><strong>stack trace for <code>Python-3.3.7</code> build failure</strong></summary>

<pre>
#7 2.773 checking build system type... x86_64-unknown-linux-gnu
#7 2.841 checking host system type... x86_64-unknown-linux-gnu
#7 2.850 checking for --enable-universalsdk... no
#7 2.853 checking for --with-universal-archs... 32-bit
#7 2.853 checking MACHDEP... linux
#7 2.863 checking for --without-gcc... no
#7 2.864 checking for gcc... gcc
#7 2.899 checking whether the C compiler works... yes
#7 2.945 checking for C compiler default output file name... a.out
#7 2.947 checking for suffix of executables...
#7 2.994 checking whether we are cross compiling... no
#7 3.043 checking for suffix of object files... o
#7 3.071 checking whether we are using the GNU C compiler... yes
#7 3.097 checking whether gcc accepts -g... yes
#7 3.124 checking for gcc option to accept ISO C89... none needed
#7 3.158 checking for --with-cxx-main=<compiler>... no
#7 3.159 checking for g++... no
#7 3.160 configure: WARNING:
#7 3.160
#7 3.160   By default, distutils will build C++ extension modules with "g++".
#7 3.160   If this is not intended, then set CXX on the configure command line.
#7 3.160
#7 3.160 checking for -Wl,--no-as-needed... yes
#7 3.207 checking how to run the C preprocessor... gcc -E
#7 3.275 checking for grep that handles long lines and -e... /bin/grep
#7 3.278 checking for egrep... /bin/grep -E
#7 3.281 checking for ANSI C header files... yes
#7 3.412 checking for sys/types.h... yes
#7 3.453 checking for sys/stat.h... yes
#7 3.497 checking for stdlib.h... yes
#7 3.539 checking for string.h... yes
#7 3.583 checking for memory.h... yes
#7 3.630 checking for strings.h... yes
#7 3.674 checking for inttypes.h... yes
#7 3.718 checking for stdint.h... yes
#7 3.762 checking for unistd.h... yes
#7 3.805 checking minix/config.h usability... no
#7 3.844 checking minix/config.h presence... no
#7 3.864 checking for minix/config.h... no
#7 3.865 checking whether it is safe to define __EXTENSIONS__... yes
#7 3.909 checking for --with-suffix...
#7 3.909 checking for case-insensitive build directory... no
#7 3.916 checking LIBRARY... libpython$(VERSION)$(ABIFLAGS).a
#7 3.916 checking LINKCC... $(PURIFY) $(MAINCC)
#7 3.917 checking for GNU ld... yes
#7 3.923 checking for inline... inline
#7 3.944 checking for --enable-shared... no
#7 3.944 checking for --enable-profiling... no
#7 3.945 checking LDLIBRARY... libpython$(VERSION)$(ABIFLAGS).a
#7 3.947 checking for ranlib... ranlib
#7 3.948 checking for ar... ar
#7 3.949 checking for readelf... readelf
#7 3.950 checking for python3.3... no
#7 3.951 checking for python3... no
#7 3.951 checking for python... no
#7 3.952 checking for a BSD-compatible install... /usr/bin/install -c
#7 3.966 checking for a thread-safe mkdir -p... /bin/mkdir -p
#7 3.970 checking for --with-pydebug... no
#7 3.985 checking whether gcc accepts and needs -fno-strict-aliasing... no
#7 4.038 checking if we can turn off gcc unused result warning... yes
#7 4.065 checking whether gcc supports ParseTuple __format__... no
#7 4.093 checking whether pthreads are available without options... no
#7 4.151 checking whether gcc accepts -Kpthread... no
#7 4.164 checking whether gcc accepts -Kthread... no
#7 4.177 checking whether gcc accepts -pthread... yes
#7 4.236 checking whether g++ also accepts flags for thread support... no
#7 4.240 checking for ANSI C header files... (cached) yes
#7 4.245 checking asm/types.h usability... yes
#7 4.282 checking asm/types.h presence... yes
#7 4.296 checking for asm/types.h... yes
#7 4.306 checking conio.h usability... no
#7 4.345 checking conio.h presence... no
#7 4.365 checking for conio.h... no
#7 4.370 checking curses.h usability... no
#7 4.410 checking curses.h presence... no
#7 4.430 checking for curses.h... no
#7 4.436 checking direct.h usability... no
#7 4.475 checking direct.h presence... no
#7 4.495 checking for direct.h... no
#7 4.500 checking dlfcn.h usability... yes
#7 4.538 checking dlfcn.h presence... yes
#7 4.552 checking for dlfcn.h... yes
#7 4.563 checking errno.h usability... yes
#7 4.601 checking errno.h presence... yes
#7 4.616 checking for errno.h... yes
#7 4.627 checking fcntl.h usability... yes
#7 4.665 checking fcntl.h presence... yes
#7 4.681 checking for fcntl.h... yes
#7 4.692 checking grp.h usability... yes
#7 4.730 checking grp.h presence... yes
#7 4.745 checking for grp.h... yes
#7 4.755 checking ieeefp.h usability... no
#7 4.794 checking ieeefp.h presence... no
#7 4.814 checking for ieeefp.h... no
#7 4.819 checking io.h usability... no
#7 4.858 checking io.h presence... no
#7 4.878 checking for io.h... no
#7 4.883 checking langinfo.h usability... yes
#7 4.921 checking langinfo.h presence... yes
#7 4.936 checking for langinfo.h... yes
#7 4.946 checking libintl.h usability... yes
#7 4.984 checking libintl.h presence... yes
#7 4.999 checking for libintl.h... yes
#7 5.009 checking ncurses.h usability... no
#7 5.048 checking ncurses.h presence... no
#7 5.068 checking for ncurses.h... no
#7 5.073 checking process.h usability... no
#7 5.116 checking process.h presence... no
#7 5.140 checking for process.h... no
#7 5.147 checking pthread.h usability... yes
#7 5.190 checking pthread.h presence... yes
#7 5.209 checking for pthread.h... yes
#7 5.219 checking sched.h usability... yes
#7 5.257 checking sched.h presence... yes
#7 5.272 checking for sched.h... yes
#7 5.283 checking shadow.h usability... yes
#7 5.320 checking shadow.h presence... yes
#7 5.335 checking for shadow.h... yes
#7 5.345 checking signal.h usability... yes
#7 5.385 checking signal.h presence... yes
#7 5.405 checking for signal.h... yes
#7 5.415 checking for stdint.h... (cached) yes
#7 5.425 checking stropts.h usability... no
#7 5.464 checking stropts.h presence... no
#7 5.484 checking for stropts.h... no
#7 5.489 checking termios.h usability... yes
#7 5.527 checking termios.h presence... yes
#7 5.543 checking for termios.h... yes
#7 5.553 checking for unistd.h... (cached) yes
#7 5.563 checking utime.h usability... yes
#7 5.600 checking utime.h presence... yes
#7 5.618 checking for utime.h... yes
#7 5.629 checking poll.h usability... yes
#7 5.666 checking poll.h presence... yes
#7 5.681 checking for poll.h... yes
#7 5.692 checking sys/devpoll.h usability... no
#7 5.731 checking sys/devpoll.h presence... no
#7 5.751 checking for sys/devpoll.h... no
#7 5.756 checking sys/epoll.h usability... yes
#7 5.794 checking sys/epoll.h presence... yes
#7 5.810 checking for sys/epoll.h... yes
#7 5.821 checking sys/poll.h usability... yes
#7 5.858 checking sys/poll.h presence... yes
#7 5.873 checking for sys/poll.h... yes
#7 5.884 checking sys/audioio.h usability... no
#7 5.923 checking sys/audioio.h presence... no
#7 5.943 checking for sys/audioio.h... no
#7 5.948 checking sys/xattr.h usability... yes
#7 5.986 checking sys/xattr.h presence... yes
#7 6.002 checking for sys/xattr.h... yes
#7 6.012 checking sys/bsdtty.h usability... no
#7 6.052 checking sys/bsdtty.h presence... no
#7 6.072 checking for sys/bsdtty.h... no
#7 6.077 checking sys/event.h usability... no
#7 6.116 checking sys/event.h presence... no
#7 6.136 checking for sys/event.h... no
#7 6.141 checking sys/file.h usability... yes
#7 6.179 checking sys/file.h presence... yes
#7 6.195 checking for sys/file.h... yes
#7 6.206 checking sys/ioctl.h usability... yes
#7 6.244 checking sys/ioctl.h presence... yes
#7 6.259 checking for sys/ioctl.h... yes
#7 6.269 checking sys/kern_control.h usability... no
#7 6.308 checking sys/kern_control.h presence... no
#7 6.328 checking for sys/kern_control.h... no
#7 6.334 checking sys/loadavg.h usability... no
#7 6.373 checking sys/loadavg.h presence... no
#7 6.395 checking for sys/loadavg.h... no
#7 6.400 checking sys/lock.h usability... no
#7 6.440 checking sys/lock.h presence... no
#7 6.460 checking for sys/lock.h... no
#7 6.465 checking sys/mkdev.h usability... no
#7 6.504 checking sys/mkdev.h presence... no
#7 6.524 checking for sys/mkdev.h... no
#7 6.529 checking sys/modem.h usability... no
#7 6.568 checking sys/modem.h presence... no
#7 6.588 checking for sys/modem.h... no
#7 6.593 checking sys/param.h usability... yes
#7 6.635 checking sys/param.h presence... yes
#7 6.655 checking for sys/param.h... yes
#7 6.665 checking sys/select.h usability... yes
#7 6.702 checking sys/select.h presence... yes
#7 6.717 checking for sys/select.h... yes
#7 6.727 checking sys/sendfile.h usability... yes
#7 6.765 checking sys/sendfile.h presence... yes
#7 6.781 checking for sys/sendfile.h... yes
#7 6.791 checking sys/socket.h usability... yes
#7 6.831 checking sys/socket.h presence... yes
#7 6.849 checking for sys/socket.h... yes
#7 6.859 checking sys/statvfs.h usability... yes
#7 6.897 checking sys/statvfs.h presence... yes
#7 6.912 checking for sys/statvfs.h... yes
#7 6.922 checking for sys/stat.h... (cached) yes
#7 6.932 checking sys/syscall.h usability... yes
#7 6.970 checking sys/syscall.h presence... yes
#7 6.984 checking for sys/syscall.h... yes
#7 6.995 checking sys/sys_domain.h usability... no
#7 7.034 checking sys/sys_domain.h presence... no
#7 7.054 checking for sys/sys_domain.h... no
#7 7.059 checking sys/termio.h usability... no
#7 7.098 checking sys/termio.h presence... no
#7 7.118 checking for sys/termio.h... no
#7 7.123 checking sys/time.h usability... yes
#7 7.161 checking sys/time.h presence... yes
#7 7.176 checking for sys/time.h... yes
#7 7.186 checking sys/times.h usability... yes
#7 7.224 checking sys/times.h presence... yes
#7 7.238 checking for sys/times.h... yes
#7 7.249 checking for sys/types.h... (cached) yes
#7 7.259 checking sys/uio.h usability... yes
#7 7.297 checking sys/uio.h presence... yes
#7 7.314 checking for sys/uio.h... yes
#7 7.324 checking sys/un.h usability... yes
#7 7.362 checking sys/un.h presence... yes
#7 7.377 checking for sys/un.h... yes
#7 7.388 checking sys/utsname.h usability... yes
#7 7.427 checking sys/utsname.h presence... yes
#7 7.441 checking for sys/utsname.h... yes
#7 7.452 checking sys/wait.h usability... yes
#7 7.493 checking sys/wait.h presence... yes
#7 7.511 checking for sys/wait.h... yes
#7 7.522 checking pty.h usability... yes
#7 7.561 checking pty.h presence... yes
#7 7.577 checking for pty.h... yes
#7 7.588 checking libutil.h usability... no
#7 7.627 checking libutil.h presence... no
#7 7.647 checking for libutil.h... no
#7 7.653 checking sys/resource.h usability... yes
#7 7.692 checking sys/resource.h presence... yes
#7 7.707 checking for sys/resource.h... yes
#7 7.718 checking netpacket/packet.h usability... yes
#7 7.756 checking netpacket/packet.h presence... yes
#7 7.769 checking for netpacket/packet.h... yes
#7 7.780 checking sysexits.h usability... yes
#7 7.817 checking sysexits.h presence... yes
#7 7.831 checking for sysexits.h... yes
#7 7.841 checking bluetooth.h usability... no
#7 7.880 checking bluetooth.h presence... no
#7 7.901 checking for bluetooth.h... no
#7 7.906 checking bluetooth/bluetooth.h usability... no
#7 7.945 checking bluetooth/bluetooth.h presence... no
#7 7.965 checking for bluetooth/bluetooth.h... no
#7 7.970 checking linux/tipc.h usability... yes
#7 8.008 checking linux/tipc.h presence... yes
#7 8.024 checking for linux/tipc.h... yes
#7 8.035 checking spawn.h usability... yes
#7 8.075 checking spawn.h presence... yes
#7 8.092 checking for spawn.h... yes
#7 8.103 checking util.h usability... no
#7 8.142 checking util.h presence... no
#7 8.162 checking for util.h... no
#7 8.167 checking alloca.h usability... yes
#7 8.205 checking alloca.h presence... yes
#7 8.219 checking for alloca.h... yes
#7 8.230 checking for dirent.h that defines DIR... yes
#7 8.269 checking for library containing opendir... none required
#7 8.317 checking whether sys/types.h defines makedev... no
#7 8.377 checking for sys/mkdev.h... (cached) no
#7 8.378 checking sys/sysmacros.h usability... yes
#7 8.417 checking sys/sysmacros.h presence... yes
#7 8.431 checking for sys/sysmacros.h... yes
#7 8.432 checking for net/if.h... yes
#7 8.568 checking for term.h... no
#7 8.591 checking for linux/netlink.h... yes
#7 8.628 checking for linux/can.h... yes
#7 8.666 checking for linux/can/raw.h... yes
#7 8.700 checking for clock_t in time.h... yes
#7 8.715 checking for makedev... yes
#7 8.765 checking Solaris LFS bug... no
#7 8.796 checking for mode_t... yes
#7 8.879 checking for off_t... yes
#7 8.947 checking for pid_t... yes
#7 9.036 checking for size_t... yes
#7 9.121 checking for uid_t in sys/types.h... yes
#7 9.138 checking for uint32_t... yes
#7 9.223 checking for uint32_t... yes
#7 9.267 checking for uint64_t... yes
#7 9.351 checking for uint64_t... yes
#7 9.398 checking for int32_t... yes
#7 9.482 checking for int32_t... yes
#7 9.566 checking for int64_t... yes
#7 9.650 checking for int64_t... yes
#7 9.734 checking for ssize_t... yes
#7 9.818 checking for __uint128_t... yes
#7 9.901 checking size of int... 4
#7 9.971 checking size of long... 8
#7 10.04 checking size of void *... 8
#7 10.11 checking size of short... 2
#7 10.18 checking size of float... 4
#7 10.25 checking size of double... 8
#7 10.32 checking size of fpos_t... 16
#7 10.39 checking size of size_t... 8
#7 10.46 checking size of pid_t... 4
#7 10.54 checking for long long support... yes
#7 10.56 checking size of long long... 8
#7 10.63 checking for long double support... yes
#7 10.66 checking size of long double... 16
#7 10.73 checking for _Bool support... yes
#7 10.76 checking size of _Bool... 1
#7 10.83 checking for uintptr_t... yes
#7 10.89 checking size of uintptr_t... 8
#7 10.96 checking size of off_t... 8
#7 11.02 checking whether to enable large file support... no
#7 11.02 checking size of time_t... 8
#7 11.08 checking for pthread_t... yes
#7 11.12 checking size of pthread_t... 8
#7 11.18 checking for --enable-framework... no
#7 11.18 checking for dyld... no
#7 11.18 checking the extension of shared libraries... .so
#7 11.18 checking LDSHARED... $(CC) -shared
#7 11.19 checking CCSHARED... -fPIC
#7 11.19 checking LINKFORSHARED... -Xlinker -export-dynamic
#7 11.19 checking CFLAGSFORSHARED...
#7 11.19 checking SHLIBS... $(LIBS)
#7 11.19 checking for sendfile in -lsendfile... no
#7 11.23 checking for dlopen in -ldl... yes
#7 11.28 checking for shl_load in -ldld... no
#7 11.32 checking for library containing sem_init... -lpthread
#7 11.43 checking for textdomain in -lintl... no
#7 11.47 checking for t_open in -lnsl... no
#7 11.53 checking for socket in -lsocket... no
#7 11.57 checking for --with-libs... no
#7 11.57 checking for pkg-config... no
#7 11.57 checking for --with-system-expat... no
#7 11.57 checking for --with-system-ffi... no
#7 11.57 checking for --with-system-libmpdec... no
#7 11.57 checking for --enable-loadable-sqlite-extensions... no
#7 11.57 checking for --with-tcltk-includes... default
#7 11.57 checking for --with-tcltk-libs... default
#7 11.57 checking for --with-dbmliborder...
#7 11.57 checking for --with-signal-module... yes
#7 11.57 checking for --with-threads... yes
#7 11.58 checking if PTHREAD_SCOPE_SYSTEM is supported... yes
#7 11.64 checking for pthread_sigmask... yes
#7 11.69 checking for pthread_atfork... yes
#7 11.75 checking if --enable-ipv6 is specified... yes
#7 11.78 checking if RFC2553 API is available... yes
#7 11.82 checking ipv6 stack type... linux-glibc
#7 11.87 checking for OSX 10.5 SDK or later... no
#7 11.89 checking for --with-doc-strings... yes
#7 11.89 checking for --with-tsc... no
#7 11.89 checking for --with-pymalloc... yes
#7 11.89 checking for --with-valgrind... no
#7 11.89 checking for dlopen... yes
#7 11.95 checking DYNLOADFILE... dynload_shlib.o
#7 11.95 checking MACHDEP_OBJS... none
#7 11.95 checking for alarm... yes
#7 12.01 checking for accept4... yes
#7 12.07 checking for setitimer... yes
#7 12.13 checking for getitimer... yes
#7 12.20 checking for bind_textdomain_codeset... yes
#7 12.26 checking for chown... yes
#7 12.32 checking for clock... yes
#7 12.38 checking for confstr... yes
#7 12.44 checking for ctermid... yes
#7 12.50 checking for execv... yes
#7 12.57 checking for faccessat... yes
#7 12.63 checking for fchmod... yes
#7 12.69 checking for fchmodat... yes
#7 12.75 checking for fchown... yes
#7 12.81 checking for fchownat... yes
#7 12.87 checking for fexecve... yes
#7 12.93 checking for fdopendir... yes
#7 12.99 checking for fork... yes
#7 13.06 checking for fpathconf... yes
#7 13.12 checking for fstatat... yes
#7 13.18 checking for ftime... yes
#7 13.24 checking for ftruncate... yes
#7 13.30 checking for futimesat... yes
#7 13.36 checking for futimens... yes
#7 13.43 checking for futimes... yes
#7 13.49 checking for gai_strerror... yes
#7 13.55 checking for getgrouplist... yes
#7 13.61 checking for getgroups... yes
#7 13.67 checking for getlogin... yes
#7 13.73 checking for getloadavg... yes
#7 13.79 checking for getpeername... yes
#7 13.86 checking for getpgid... yes
#7 13.92 checking for getpid... yes
#7 13.98 checking for getpriority... yes
#7 14.04 checking for getresuid... yes
#7 14.10 checking for getresgid... yes
#7 14.16 checking for getpwent... yes
#7 14.22 checking for getspnam... yes
#7 14.28 checking for getspent... yes
#7 14.34 checking for getsid... yes
#7 14.41 checking for getwd... yes
#7 14.47 checking for if_nameindex... yes
#7 14.53 checking for initgroups... yes
#7 14.60 checking for kill... yes
#7 14.66 checking for killpg... yes
#7 14.72 checking for lchmod... no
#7 14.75 checking for lchown... yes
#7 14.81 checking for lockf... yes
#7 14.87 checking for linkat... yes
#7 14.93 checking for lstat... yes
#7 15.00 checking for lutimes... yes
#7 15.06 checking for mmap... yes
#7 15.12 checking for memrchr... yes
#7 15.18 checking for mbrtowc... yes
#7 15.24 checking for mkdirat... yes
#7 15.30 checking for mkfifo... yes
#7 15.36 checking for mkfifoat... yes
#7 15.42 checking for mknod... yes
#7 15.49 checking for mknodat... yes
#7 15.55 checking for mktime... yes
#7 15.61 checking for mremap... yes
#7 15.67 checking for nice... yes
#7 15.73 checking for openat... yes
#7 15.80 checking for pathconf... yes
#7 15.86 checking for pause... yes
#7 15.92 checking for pipe2... yes
#7 15.98 checking for plock... no
#7 16.04 checking for poll... yes
#7 16.10 checking for posix_fallocate... yes
#7 16.17 checking for posix_fadvise... yes
#7 16.23 checking for pread... yes
#7 16.29 checking for pthread_init... no
#7 16.35 checking for pthread_kill... yes
#7 16.41 checking for putenv... yes
#7 16.47 checking for pwrite... yes
#7 16.53 checking for readlink... yes
#7 16.60 checking for readlinkat... yes
#7 16.66 checking for readv... yes
#7 16.72 checking for realpath... yes
#7 16.78 checking for renameat... yes
#7 16.84 checking for select... yes
#7 16.90 checking for sem_open... yes
#7 16.96 checking for sem_timedwait... yes
#7 17.02 checking for sem_getvalue... yes
#7 17.09 checking for sem_unlink... yes
#7 17.15 checking for sendfile... yes
#7 17.21 checking for setegid... yes
#7 17.27 checking for seteuid... yes
#7 17.33 checking for setgid... yes
#7 17.39 checking for sethostname... yes
#7 17.45 checking for setlocale... yes
#7 17.51 checking for setregid... yes
#7 17.57 checking for setreuid... yes
#7 17.64 checking for setresuid... yes
#7 17.70 checking for setresgid... yes
#7 17.76 checking for setsid... yes
#7 17.82 checking for setpgid... yes
#7 17.88 checking for setpgrp... yes
#7 17.94 checking for setpriority... yes
#7 18.00 checking for setuid... yes
#7 18.06 checking for setvbuf... yes
#7 18.12 checking for sched_get_priority_max... yes
#7 18.18 checking for sched_setaffinity... yes
#7 18.24 checking for sched_setscheduler... yes
#7 18.31 checking for sched_setparam... yes
#7 18.37 checking for sched_rr_get_interval... yes
#7 18.43 checking for sigaction... yes
#7 18.49 checking for sigaltstack... yes
#7 18.55 checking for siginterrupt... yes
#7 18.61 checking for sigpending... yes
#7 18.67 checking for sigrelse... yes
#7 18.73 checking for sigtimedwait... yes
#7 18.79 checking for sigwait... yes
#7 18.85 checking for sigwaitinfo... yes
#7 18.92 checking for snprintf... yes
#7 18.98 checking for strftime... yes
#7 19.05 checking for strlcpy... no
#7 19.11 checking for symlinkat... yes
#7 19.17 checking for sync... yes
#7 19.23 checking for sysconf... yes
#7 19.30 checking for tcgetpgrp... yes
#7 19.36 checking for tcsetpgrp... yes
#7 19.42 checking for tempnam... yes
#7 19.48 checking for timegm... yes
#7 19.54 checking for times... yes
#7 19.61 checking for tmpfile... yes
#7 19.67 checking for tmpnam... yes
#7 19.73 checking for tmpnam_r... yes
#7 19.80 checking for truncate... yes
#7 19.86 checking for uname... yes
#7 19.92 checking for unlinkat... yes
#7 19.98 checking for unsetenv... yes
#7 20.04 checking for utimensat... yes
#7 20.10 checking for utimes... yes
#7 20.16 checking for waitid... yes
#7 20.22 checking for waitpid... yes
#7 20.29 checking for wait3... yes
#7 20.35 checking for wait4... yes
#7 20.41 checking for wcscoll... yes
#7 20.47 checking for wcsftime... yes
#7 20.53 checking for wcsxfrm... yes
#7 20.60 checking for writev... yes
#7 20.66 checking for _getpty... no
#7 20.72 checking whether dirfd is declared... yes
#7 20.75 checking for chroot... yes
#7 20.79 checking for link... yes
#7 20.82 checking for symlink... yes
#7 20.85 checking for fchdir... yes
#7 20.88 checking for fsync... yes
#7 20.91 checking for fdatasync... yes
#7 20.94 checking for epoll... yes
#7 20.98 checking for epoll_create1... yes
#7 21.01 checking for kqueue... no
#7 21.03 checking for ctermid_r... no
#7 21.06 checking for flock declaration... yes
#7 21.09 checking for flock... yes
#7 21.15 checking for getpagesize... yes
#7 21.18 checking for broken unsetenv... no
#7 21.21 checking for true... true
#7 21.21 checking for inet_aton in -lc... yes
#7 21.26 checking for chflags... no
#7 21.32 checking for lchflags... no
#7 21.38 checking for inflateCopy in -lz... no
#7 21.43 checking for hstrerror... yes
#7 21.48 checking for inet_aton... yes
#7 21.54 checking for inet_pton... yes
#7 21.58 checking for setgroups... yes
#7 21.61 checking for openpty... no
#7 21.67 checking for openpty in -lutil... yes
#7 21.72 checking for forkpty... yes
#7 21.78 checking for memmove... yes
#7 21.84 checking for fseek64... no
#7 21.90 checking for fseeko... yes
#7 21.96 checking for fstatvfs... yes
#7 22.03 checking for ftell64... no
#7 22.09 checking for ftello... yes
#7 22.15 checking for statvfs... yes
#7 22.21 checking for dup2... yes
#7 22.26 checking for getcwd... yes
#7 22.31 checking for strdup... yes
#7 22.37 checking for getpgrp... yes
#7 22.45 checking for setpgrp... (cached) yes
#7 22.48 checking for gettimeofday... yes
#7 22.56 checking for clock_gettime... yes
#7 22.62 checking for clock_getres... yes
#7 22.67 checking for major... yes
#7 22.72 checking for getaddrinfo... yes
#7 22.79 checking getaddrinfo bug... no
#7 22.85 checking for getnameinfo... yes
#7 22.91 checking whether time.h and sys/time.h may both be included... yes
#7 22.94 checking whether struct tm is in sys/time.h or time.h... time.h
#7 22.97 checking for struct tm.tm_zone... yes
#7 23.00 checking for struct stat.st_rdev... yes
#7 23.05 checking for struct stat.st_blksize... yes
#7 23.10 checking for struct stat.st_flags... no
#7 23.18 checking for struct stat.st_gen... no
#7 23.26 checking for struct stat.st_birthtime... no
#7 23.34 checking for struct stat.st_blocks... yes
#7 23.39 checking for time.h that defines altzone... no
#7 23.42 checking whether sys/select.h and sys/time.h may both be included... yes
#7 23.45 checking for addrinfo... yes
#7 23.48 checking for sockaddr_storage... yes
#7 23.52 checking whether char is unsigned... no
#7 23.56 checking for an ANSI C-conforming const... yes
#7 23.59 checking for working volatile... yes
#7 23.62 checking for working signed char... yes
#7 23.64 checking for prototypes... yes
#7 23.67 checking for variable length prototypes and stdarg.h... yes
#7 23.70 checking for socketpair... yes
#7 23.74 checking if sockaddr has sa_len member... no
#7 23.77 checking whether va_list is an array... yes
#7 23.79 checking for gethostbyname_r... yes
#7 23.84 checking gethostbyname_r with 6 args... yes
#7 23.88 checking for __fpu_control... yes
#7 23.93 checking for --with-fpectl... no
#7 23.93 checking for --with-libm=STRING... default LIBM="-lm"
#7 23.93 checking for --with-libc=STRING... default LIBC=""
#7 23.93 checking for x64 gcc inline assembler... yes
#7 23.96 checking whether C doubles are little-endian IEEE 754 binary64... yes
#7 24.02 checking whether C doubles are big-endian IEEE 754 binary64... no
#7 24.07 checking whether C doubles are ARM mixed-endian IEEE 754 binary64... no
#7 24.13 checking whether we can use gcc inline assembler to get and set x87 control word... yes
#7 24.16 checking for x87-style double rounding... no
#7 24.24 checking for acosh... yes
#7 24.32 checking for asinh... yes
#7 24.39 checking for atanh... yes
#7 24.47 checking for copysign... yes
#7 24.54 checking for erf... yes
#7 24.61 checking for erfc... yes
#7 24.69 checking for expm1... yes
#7 24.76 checking for finite... yes
#7 24.84 checking for gamma... yes
#7 24.91 checking for hypot... yes
#7 24.98 checking for lgamma... yes
#7 25.06 checking for log1p... yes
#7 25.13 checking for log2... yes
#7 25.20 checking for round... yes
#7 25.28 checking for tgamma... yes
#7 25.35 checking whether isinf is declared... yes
#7 25.42 checking whether isnan is declared... yes
#7 25.48 checking whether isfinite is declared... yes
#7 25.53 checking whether tanh preserves the sign of zero... yes
#7 25.62 checking whether log1p drops the sign of negative zero... no
#7 25.70 checking whether POSIX semaphores are enabled... yes
#7 25.76 checking for broken sem_getvalue... no
#7 25.83 checking digit size for Python's longs... no value specified
#7 25.83 checking wchar.h usability... yes
#7 25.87 checking wchar.h presence... yes
#7 25.89 checking for wchar.h... yes
#7 25.89 checking size of wchar_t... 4
#7 25.95 checking for UCS-4 tcl... no
#7 25.98 checking whether wchar_t is signed... yes
#7 26.03 no usable wchar_t found
#7 26.03 checking whether byte ordering is bigendian... no
#7 26.12 checking ABIFLAGS... m
#7 26.12 checking SOABI... cpython-33m
#7 26.12 checking LDVERSION... $(VERSION)$(ABIFLAGS)
#7 26.12 checking whether right shift extends the sign bit... yes
#7 26.18 checking for getc_unlocked() and friends... yes
#7 26.23 checking how to link readline libs... none
#7 26.49 checking for rl_callback_handler_install in -lreadline... no
#7 26.55 checking for rl_pre_input_hook in -lreadline... no
#7 26.60 checking for rl_completion_display_matches_hook in -lreadline... no
#7 26.65 checking for rl_completion_matches in -lreadline... no
#7 26.71 checking for broken nice()... no
#7 26.76 checking for broken poll()... no
#7 26.82 checking for struct tm.tm_zone... (cached) yes
#7 26.82 checking for working tzset()... yes
#7 26.89 checking for tv_nsec in struct stat... yes
#7 26.92 checking for tv_nsec2 in struct stat... no
#7 26.95 checking whether mvwdelch is an expression... no
#7 26.97 checking whether WINDOW has _flags... no
#7 26.99 checking for is_term_resized... no
#7 27.02 checking for resize_term... no
#7 27.04 checking for resizeterm... no
#7 27.06 configure: checking for device files
#7 27.06 checking for /dev/ptmx... yes
#7 27.07 checking for /dev/ptc... no
#7 27.07 checking for %lld and %llu printf() format support... yes
#7 27.13 checking for %zd printf() format support... yes
#7 27.19 checking for socklen_t... yes
#7 27.25 checking for broken mbstowcs... no
#7 27.31 checking for --with-computed-gotos... no value specified
#7 27.31 checking whether gcc -pthread supports computed gotos... yes
#7 27.36 checking for build directories... done
#7 27.36 checking for -O2... yes
#7 27.39 checking for glibc _FORTIFY_SOURCE/memmove bug... no
#7 27.47 checking for gcc ipa-pure-const bug... no
#7 27.56 configure: creating ./config.status
#7 27.69 config.status: creating Makefile.pre
#7 27.71 config.status: creating Modules/Setup.config
#7 27.73 config.status: creating Misc/python.pc
#7 27.76 config.status: creating Modules/ld_so_aix
#7 27.78 config.status: creating pyconfig.h
#7 27.80 creating Modules/Setup
#7 27.80 creating Modules/Setup.local
#7 27.80 creating Makefile
#7 27.98 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Modules/python.o ./Modules/python.c
#7 28.09 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/acceler.o Parser/acceler.c
#7 28.23 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/grammar1.o Parser/grammar1.c
#7 28.33 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/listnode.o Parser/listnode.c
#7 28.53 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/node.o Parser/node.c
#7 28.72 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/parser.o Parser/parser.c
#7 28.88 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/bitset.o Parser/bitset.c
#7 29.00 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/metagrammar.o Parser/metagrammar.c
#7 29.10 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/firstsets.o Parser/firstsets.c
#7 29.23 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/grammar.o Parser/grammar.c
#7 29.39 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/pgen.o Parser/pgen.c
#7 29.82 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/myreadline.o Parser/myreadline.c
#7 29.94 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/parsetok.o Parser/parsetok.c
#7 30.15 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Parser/tokenizer.o Parser/tokenizer.c
#7 30.76 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/abstract.o Objects/abstract.c
#7 32.43 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/accu.o Objects/accu.c
#7 32.57 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/boolobject.o Objects/boolobject.c
#7 32.68 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/bytes_methods.o Objects/bytes_methods.c
#7 32.89 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/bytearrayobject.o Objects/bytearrayobject.c
#7 34.88 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/bytesobject.o Objects/bytesobject.c
#7 34.95 In file included from Include/Python.h:69,
#7 34.95                  from Objects/bytesobject.c:5:
#7 34.95 Objects/bytesobject.c: In function 'PyBytes_FromStringAndSize':
#7 34.95 Include/objimpl.h:163:66: warning: right-hand operand of comma expression has no effect [-Wunused-value]
#7 34.95   163 |     ( Py_TYPE(op) = (typeobj), _Py_NewReference((PyObject *)(op)), (op) )
#7 34.95       |     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^~~~~~~~
#7 34.95 Include/objimpl.h:165:29: note: in expansion of macro 'PyObject_INIT'
#7 34.95   165 |     ( Py_SIZE(op) = (size), PyObject_INIT((op), (typeobj)) )
#7 34.95       |                             ^~~~~~~~~~~~~
#7 34.95 Objects/bytesobject.c:101:5: note: in expansion of macro 'PyObject_INIT_VAR'
#7 34.95   101 |     PyObject_INIT_VAR(op, &PyBytes_Type, size);
#7 34.95       |     ^~~~~~~~~~~~~~~~~
#7 34.95 Objects/bytesobject.c: In function 'PyBytes_FromString':
#7 34.95 Include/objimpl.h:163:66: warning: right-hand operand of comma expression has no effect [-Wunused-value]
#7 34.95   163 |     ( Py_TYPE(op) = (typeobj), _Py_NewReference((PyObject *)(op)), (op) )
#7 34.95       |     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^~~~~~~~
#7 34.95 Include/objimpl.h:165:29: note: in expansion of macro 'PyObject_INIT'
#7 34.95   165 |     ( Py_SIZE(op) = (size), PyObject_INIT((op), (typeobj)) )
#7 34.95       |                             ^~~~~~~~~~~~~
#7 34.95 Objects/bytesobject.c:149:5: note: in expansion of macro 'PyObject_INIT_VAR'
#7 34.95   149 |     PyObject_INIT_VAR(op, &PyBytes_Type, size);
#7 34.95       |     ^~~~~~~~~~~~~~~~~
#7 34.96 Objects/bytesobject.c: In function 'bytes_repeat':
#7 34.96 Include/objimpl.h:163:66: warning: right-hand operand of comma expression has no effect [-Wunused-value]
#7 34.96   163 |     ( Py_TYPE(op) = (typeobj), _Py_NewReference((PyObject *)(op)), (op) )
#7 34.96       |     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^~~~~~~~
#7 34.96 Include/objimpl.h:165:29: note: in expansion of macro 'PyObject_INIT'
#7 34.96   165 |     ( Py_SIZE(op) = (size), PyObject_INIT((op), (typeobj)) )
#7 34.96       |                             ^~~~~~~~~~~~~
#7 34.96 Objects/bytesobject.c:759:5: note: in expansion of macro 'PyObject_INIT_VAR'
#7 34.96   759 |     PyObject_INIT_VAR(op, &PyBytes_Type, size);
#7 34.96       |     ^~~~~~~~~~~~~~~~~
#7 36.91 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/cellobject.o Objects/cellobject.c
#7 37.04 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/classobject.o Objects/classobject.c
#7 37.11 In file included from Include/Python.h:69,
#7 37.11                  from Objects/classobject.c:3:
#7 37.11 Objects/classobject.c: In function 'PyMethod_New':
#7 37.11 Include/objimpl.h:163:66: warning: right-hand operand of comma expression has no effect [-Wunused-value]
#7 37.11   163 |     ( Py_TYPE(op) = (typeobj), _Py_NewReference((PyObject *)(op)), (op) )
#7 37.11       |     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^~~~~~~~
#7 37.11 Objects/classobject.c:55:9: note: in expansion of macro 'PyObject_INIT'
#7 37.11    55 |         PyObject_INIT(im, &PyMethod_Type);
#7 37.11       |         ^~~~~~~~~~~~~
#7 37.30 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/codeobject.o Objects/codeobject.c
#7 37.59 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/complexobject.o Objects/complexobject.c
#7 37.66 In file included from Include/Python.h:69,
#7 37.66                  from Objects/complexobject.c:8:
#7 37.66 Objects/complexobject.c: In function 'PyComplex_FromCComplex':
#7 37.66 Include/objimpl.h:163:66: warning: right-hand operand of comma expression has no effect [-Wunused-value]
#7 37.66   163 |     ( Py_TYPE(op) = (typeobj), _Py_NewReference((PyObject *)(op)), (op) )
#7 37.66       |     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^~~~~~~~
#7 37.66 Objects/complexobject.c:220:5: note: in expansion of macro 'PyObject_INIT'
#7 37.66   220 |     PyObject_INIT(op, &PyComplex_Type);
#7 37.66       |     ^~~~~~~~~~~~~
#7 38.07 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/descrobject.o Objects/descrobject.c
#7 38.57 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/enumobject.o Objects/enumobject.c
#7 38.75 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/exceptions.o Objects/exceptions.c
#7 39.82 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/genobject.o Objects/genobject.c
#7 40.10 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/fileobject.o Objects/fileobject.c
#7 40.31 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/floatobject.o Objects/floatobject.c
#7 40.38 In file included from Include/Python.h:69,
#7 40.38                  from Objects/floatobject.c:7:
#7 40.38 Objects/floatobject.c: In function 'PyFloat_FromDouble':
#7 40.38 Include/objimpl.h:163:66: warning: right-hand operand of comma expression has no effect [-Wunused-value]
#7 40.38   163 |     ( Py_TYPE(op) = (typeobj), _Py_NewReference((PyObject *)(op)), (op) )
#7 40.38       |     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^~~~~~~~
#7 40.38 Objects/floatobject.c:127:5: note: in expansion of macro 'PyObject_INIT'
#7 40.38   127 |     PyObject_INIT(op, &PyFloat_Type);
#7 40.38       |     ^~~~~~~~~~~~~
#7 41.08 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/frameobject.o Objects/frameobject.c
#7 41.44 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/funcobject.o Objects/funcobject.c
#7 41.80 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/iterobject.o Objects/iterobject.c
#7 41.96 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/listobject.o Objects/listobject.c
#7 42.03 In file included from Include/Python.h:66,
#7 42.03                  from Objects/listobject.c:3:
#7 42.03 Objects/listobject.c: In function 'list_resize':
#7 42.03 Include/pymem.h:110:34: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#7 42.03   110 |  (type *) PyMem_REALLOC((p), (n) * sizeof(type)) )
#7 42.03       |                                  ^
#7 42.03 Include/pymem.h:77:21: note: in definition of macro 'PyMem_REALLOC'
#7 42.03    77 |     : realloc((p), (n) ? (n) : 1))
#7 42.03       |                     ^
#7 42.03 Objects/listobject.c:63:9: note: in expansion of macro 'PyMem_RESIZE'
#7 42.03    63 |         PyMem_RESIZE(items, PyObject *, new_allocated);
#7 42.03       |         ^~~~~~~~~~~~
#7 42.05 Objects/listobject.c: In function 'listsort':
#7 42.05 Objects/listobject.c:1955:52: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#7 42.05  1955 |             keys = PyMem_MALLOC(sizeof(PyObject *) * saved_ob_size);
#7 42.05 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#7 42.05    75 |     : malloc((n) ? (n) : 1))
#7 42.05       |               ^
#7 42.05 Objects/listobject.c: In function 'list_ass_subscript':
#7 42.05 Objects/listobject.c:2495:41: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#7 42.05  2495 |                 PyMem_MALLOC(slicelength*sizeof(PyObject*));
#7 42.05 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#7 42.05    75 |     : malloc((n) ? (n) : 1))
#7 42.05       |               ^
#7 42.05 Objects/listobject.c:2576:41: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#7 42.05  2576 |                 PyMem_MALLOC(slicelength*sizeof(PyObject*));
#7 42.05 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#7 42.05    75 |     : malloc((n) ? (n) : 1))
#7 42.05       |               ^
#7 43.18 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/longobject.o Objects/longobject.c
#7 43.32 In file included from Include/Python.h:69,
#7 43.32                  from Objects/longobject.c:5:
#7 43.32 Objects/longobject.c: In function '_PyLong_Init':
#7 43.32 Include/objimpl.h:163:66: warning: right-hand operand of comma expression has no effect [-Wunused-value]
#7 43.32   163 |     ( Py_TYPE(op) = (typeobj), _Py_NewReference((PyObject *)(op)), (op) )
#7 43.32       |     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^~~~~~~~
#7 43.32 Objects/longobject.c:5085:13: note: in expansion of macro 'PyObject_INIT'
#7 43.32  5085 |             PyObject_INIT(v, &PyLong_Type);
#7 43.32       |             ^~~~~~~~~~~~~
#7 45.46 Objects/longobject.c: In function '_PyLong_Frexp':
#7 45.46 Objects/longobject.c:2649:33: warning: 'x_digits[0]' may be used uninitialized in this function [-Wmaybe-uninitialized]
#7 45.46  2649 |                     x_digits[0] |= 1;
#7 45.46       |                                 ^~
#7 45.73 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/dictobject.o Objects/dictobject.c
#7 45.80 In file included from Include/Python.h:66,
#7 45.80                  from Objects/dictobject.c:69:
#7 45.80 Objects/dictobject.c: In function 'new_dict_with_shared_keys':
#7 45.80 Include/pymem.h:97:30: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#7 45.80    97 |  ( (type *) PyMem_MALLOC((n) * sizeof(type)) ) )
#7 45.80       |                              ^
#7 45.80 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#7 45.80    75 |     : malloc((n) ? (n) : 1))
#7 45.80       |               ^
#7 45.80 Objects/dictobject.c:383:26: note: in expansion of macro 'PyMem_NEW'
#7 45.80   383 | #define new_values(size) PyMem_NEW(PyObject *, size)
#7 45.80       |                          ^~~~~~~~~
#7 45.80 Objects/dictobject.c:420:14: note: in expansion of macro 'new_values'
#7 45.80   420 |     values = new_values(size);
#7 45.80       |              ^~~~~~~~~~
#7 45.80 Objects/dictobject.c: In function 'make_keys_shared':
#7 45.80 Include/pymem.h:97:30: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#7 45.80    97 |  ( (type *) PyMem_MALLOC((n) * sizeof(type)) ) )
#7 45.80       |                              ^
#7 45.80 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#7 45.80    75 |     : malloc((n) ? (n) : 1))
#7 45.80       |               ^
#7 45.80 Objects/dictobject.c:383:26: note: in expansion of macro 'PyMem_NEW'
#7 45.80   383 | #define new_values(size) PyMem_NEW(PyObject *, size)
#7 45.80       |                          ^~~~~~~~~
#7 45.80 Objects/dictobject.c:1025:18: note: in expansion of macro 'new_values'
#7 45.80  1025 |         values = new_values(size);
#7 45.80       |                  ^~~~~~~~~~
#7 45.81 Objects/dictobject.c: In function 'PyDict_Copy':
#7 45.82 Include/pymem.h:97:30: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#7 45.82    97 |  ( (type *) PyMem_MALLOC((n) * sizeof(type)) ) )
#7 45.82       |                              ^
#7 45.82 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#7 45.82    75 |     : malloc((n) ? (n) : 1))
#7 45.82       |               ^
#7 45.82 Objects/dictobject.c:383:26: note: in expansion of macro 'PyMem_NEW'
#7 45.82   383 | #define new_values(size) PyMem_NEW(PyObject *, size)
#7 45.82       |                          ^~~~~~~~~
#7 45.82 Objects/dictobject.c:2053:32: note: in expansion of macro 'new_values'
#7 45.82  2053 |         PyObject **newvalues = new_values(DK_SIZE(mp->ma_keys));
#7 45.82       |                                ^~~~~~~~~~
#7 47.06 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/memoryobject.o Objects/memoryobject.c
#7 48.09 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/methodobject.o Objects/methodobject.c
#7 48.16 In file included from Include/Python.h:69,
#7 48.16                  from Objects/methodobject.c:4:
#7 48.16 Objects/methodobject.c: In function 'PyCFunction_NewEx':
#7 48.16 Include/objimpl.h:163:66: warning: right-hand operand of comma expression has no effect [-Wunused-value]
#7 48.16   163 |     ( Py_TYPE(op) = (typeobj), _Py_NewReference((PyObject *)(op)), (op) )
#7 48.16       |     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^~~~~~~~
#7 48.16 Objects/methodobject.c:23:9: note: in expansion of macro 'PyObject_INIT'
#7 48.16    23 |         PyObject_INIT(op, &PyCFunction_Type);
#7 48.16       |         ^~~~~~~~~~~~~
#7 48.27 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/moduleobject.o Objects/moduleobject.c
#7 48.55 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/namespaceobject.o Objects/namespaceobject.c
#7 48.70 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/object.o Objects/object.c
#7 49.29 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/obmalloc.o Objects/obmalloc.c
#7 49.52 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/capsule.o Objects/capsule.c
#7 49.68 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/rangeobject.o Objects/rangeobject.c
#7 50.16 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/setobject.o Objects/setobject.c
#7 50.24 In file included from Include/Python.h:66,
#7 50.24                  from Objects/setobject.c:7:
#7 50.24 Objects/setobject.c: In function 'set_table_resize':
#7 50.24 Include/pymem.h:97:30: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#7 50.24    97 |  ( (type *) PyMem_MALLOC((n) * sizeof(type)) ) )
#7 50.24       |                              ^
#7 50.24 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#7 50.24    75 |     : malloc((n) ? (n) : 1))
#7 50.24       |               ^
#7 50.24 Objects/setobject.c:318:20: note: in expansion of macro 'PyMem_NEW'
#7 50.24   318 |         newtable = PyMem_NEW(setentry, newsize);
#7 50.24       |                    ^~~~~~~~~
#7 51.25 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/sliceobject.o Objects/sliceobject.c
#7 51.45 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/structseq.o Objects/structseq.c
#7 51.52 In file included from Include/Python.h:66,
#7 51.52                  from Objects/structseq.c:4:
#7 51.52 Objects/structseq.c: In function 'PyStructSequence_InitType':
#7 51.52 Include/pymem.h:97:30: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#7 51.52    97 |  ( (type *) PyMem_MALLOC((n) * sizeof(type)) ) )
#7 51.52       |                              ^
#7 51.52 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#7 51.52    75 |     : malloc((n) ? (n) : 1))
#7 51.52       |               ^
#7 51.52 Objects/structseq.c:344:15: note: in expansion of macro 'PyMem_NEW'
#7 51.52   344 |     members = PyMem_NEW(PyMemberDef, n_members-n_unnamed_members+1);
#7 51.52       |               ^~~~~~~~~
#7 51.56 Objects/structseq.c: In function 'structseq_repr':
#7 51.56 Objects/structseq.c:175:5: warning: 'strncpy' specified bound depends on the length of the source argument [-Wstringop-overflow=]
#7 51.56   175 |     strncpy(pbuf, typ->tp_name, len);
#7 51.56       |     ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#7 51.56 Objects/structseq.c:173:11: note: length computed here
#7 51.56   173 |     len = strlen(typ->tp_name) > TYPE_MAXSIZE ? TYPE_MAXSIZE :
#7 51.56       |           ^~~~~~~~~~~~~~~~~~~~
#7 51.69 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/tupleobject.o Objects/tupleobject.c
#7 52.13 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/typeobject.o Objects/typeobject.c
#7 52.21 In file included from Include/Python.h:69,
#7 52.21                  from Objects/typeobject.c:3:
#7 52.21 Objects/typeobject.c: In function 'PyType_GenericAlloc':
#7 52.21 Include/objimpl.h:163:66: warning: right-hand operand of comma expression has no effect [-Wunused-value]
#7 52.21   163 |     ( Py_TYPE(op) = (typeobj), _Py_NewReference((PyObject *)(op)), (op) )
#7 52.21       |     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^~~~~~~~
#7 52.21 Objects/typeobject.c:773:9: note: in expansion of macro 'PyObject_INIT'
#7 52.21   773 |         PyObject_INIT(obj, type);
#7 52.21       |         ^~~~~~~~~~~~~
#7 52.21 In file included from Include/Python.h:66,
#7 52.21                  from Objects/typeobject.c:3:
#7 52.21 Objects/typeobject.c: In function 'pmerge':
#7 52.21 Objects/typeobject.c:1448:44: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#7 52.21  1448 |     remain = (int *)PyMem_MALLOC(SIZEOF_INT*to_merge_size);
#7 52.21 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#7 52.21    75 |     : malloc((n) ? (n) : 1))
#7 52.21       |               ^
#7 54.82 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/unicodeobject.o Objects/unicodeobject.c
#7 54.96 In file included from Include/Python.h:66,
#7 54.96                  from Objects/unicodeobject.c:42:
#7 54.96 Objects/unicodeobject.c: In function 'PyUnicode_AsWideCharString':
#7 54.96 Objects/unicodeobject.c:2956:34: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#7 54.96  2956 |     buffer = PyMem_MALLOC(buflen * sizeof(wchar_t));
#7 54.96 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#7 54.96    75 |     : malloc((n) ? (n) : 1))
#7 54.96       |               ^
#7 55.10 Objects/unicodeobject.c: In function '_PyUnicode_TranslateCharmap':
#7 55.10 Include/pymem.h:97:30: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#7 55.10    97 |  ( (type *) PyMem_MALLOC((n) * sizeof(type)) ) )
#7 55.10       |                              ^
#7 55.10 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#7 55.10    75 |     : malloc((n) ? (n) : 1))
#7 55.10       |               ^
#7 55.10 Objects/unicodeobject.c:8509:14: note: in expansion of macro 'PyMem_NEW'
#7 55.10  8509 |     output = PyMem_NEW(Py_UCS4, osize);
#7 55.10       |              ^~~~~~~~~
#7 55.14 Objects/unicodeobject.c: In function 'case_operation':
#7 55.14 Objects/unicodeobject.c:9498:44: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#7 55.14  9498 |     tmp = PyMem_MALLOC(sizeof(Py_UCS4) * 3 * length);
#7 55.14 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#7 55.14    75 |     : malloc((n) ? (n) : 1))
#7 55.14       |               ^
#7 67.14 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/unicodectype.o Objects/unicodectype.c
#7 67.61 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Objects/weakrefobject.o Objects/weakrefobject.c
#7 68.24 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/_warnings.o Python/_warnings.c
#7 68.64 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/Python-ast.o Python/Python-ast.c
#7 71.69 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/asdl.o Python/asdl.c
#7 71.79 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/ast.o Python/ast.c
#7 73.23 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/bltinmodule.o Python/bltinmodule.c
#7 73.94 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/ceval.o Python/ceval.c
#7 77.29 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/compile.o Python/compile.c
#7 77.97 In function 'assemble_lnotab',
#7 77.97     inlined from 'assemble_emit' at Python/compile.c:3952:25,
#7 77.97     inlined from 'assemble' at Python/compile.c:4239:18:
#7 77.97 Python/compile.c:3903:19: warning: writing 1 byte into a region of size 0 [-Wstringop-overflow=]
#7 77.97  3903 |         *lnotab++ = 255;
#7 77.97       |         ~~~~~~~~~~^~~~~
#7 79.17 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/codecs.o Python/codecs.c
#7 79.73 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/dynamic_annotations.o Python/dynamic_annotations.c
#7 79.76 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/errors.o Python/errors.c
#7 80.22 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/frozenmain.o Python/frozenmain.c
#7 80.34 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/future.o Python/future.c
#7 80.46 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/getargs.o Python/getargs.c
#7 80.54 In file included from Include/Python.h:66,
#7 80.54                  from Python/getargs.c:4:
#7 80.54 Python/getargs.c: In function 'vgetargs1':
#7 80.54 Include/pymem.h:97:30: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#7 80.54    97 |  ( (type *) PyMem_MALLOC((n) * sizeof(type)) ) )
#7 80.54       |                              ^
#7 80.54 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#7 80.54    75 |     : malloc((n) ? (n) : 1))
#7 80.54       |               ^
#7 80.54 Python/getargs.c:265:24: note: in expansion of macro 'PyMem_NEW'
#7 80.54   265 |     freelist.entries = PyMem_NEW(freelistentry_t, max);
#7 80.54       |                        ^~~~~~~~~
#7 80.54 Python/getargs.c: In function 'convertsimple':
#7 80.54 Include/pymem.h:97:30: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#7 80.54    97 |  ( (type *) PyMem_MALLOC((n) * sizeof(type)) ) )
#7 80.54       |                              ^
#7 80.54 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#7 80.54    75 |     : malloc((n) ? (n) : 1))
#7 80.54       |               ^
#7 80.54 Python/getargs.c:1091:27: note: in expansion of macro 'PyMem_NEW'
#7 80.54  1091 |                 *buffer = PyMem_NEW(char, size + 1);
#7 80.54       |                           ^~~~~~~~~
#7 80.54 Include/pymem.h:97:30: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#7 80.54    97 |  ( (type *) PyMem_MALLOC((n) * sizeof(type)) ) )
#7 80.54       |                              ^
#7 80.54 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#7 80.54    75 |     : malloc((n) ? (n) : 1))
#7 80.54       |               ^
#7 80.54 Python/getargs.c:1133:23: note: in expansion of macro 'PyMem_NEW'
#7 80.54  1133 |             *buffer = PyMem_NEW(char, size + 1);
#7 80.54       |                       ^~~~~~~~~
#7 80.55 Python/getargs.c: In function 'vgetargskeywords':
#7 80.55 Include/pymem.h:97:30: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#7 80.55    97 |  ( (type *) PyMem_MALLOC((n) * sizeof(type)) ) )
#7 80.55       |                              ^
#7 80.55 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#7 80.55    75 |     : malloc((n) ? (n) : 1))
#7 80.55       |               ^
#7 80.55 Python/getargs.c:1448:24: note: in expansion of macro 'PyMem_NEW'
#7 80.55  1448 |     freelist.entries = PyMem_NEW(freelistentry_t, len);
#7 80.55       |                        ^~~~~~~~~
#7 81.34 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/getcompiler.o Python/getcompiler.c
#7 81.43 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/getcopyright.o Python/getcopyright.c
#7 81.52 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -DPLATFORM='"linux"' -o Python/getplatform.o ./Python/getplatform.c
#7 81.61 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/getversion.o Python/getversion.c
#7 81.69 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/graminit.o Python/graminit.c
#7 81.79 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/import.o Python/import.c
#7 81.89 In file included from Include/Python.h:66,
#7 81.89                  from Python/import.c:4:
#7 81.89 Python/import.c: In function 'PyImport_ExtendInittab':
#7 81.89 Include/pymem.h:110:34: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#7 81.89   110 |  (type *) PyMem_REALLOC((p), (n) * sizeof(type)) )
#7 81.89       |                                  ^
#7 81.89 Include/pymem.h:77:21: note: in definition of macro 'PyMem_REALLOC'
#7 81.89    77 |     : realloc((p), (n) ? (n) : 1))
#7 81.89       |                     ^
#7 81.89 Python/import.c:1916:5: note: in expansion of macro 'PyMem_RESIZE'
#7 81.89  1916 |     PyMem_RESIZE(p, struct _inittab, i+n+1);
#7 81.89       |     ^~~~~~~~~~~~
#7 82.44 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -I. -o Python/importdl.o ./Python/importdl.c
#7 82.55 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/marshal.o Python/marshal.c
#7 82.63 In file included from Include/Python.h:66,
#7 82.63                  from Python/marshal.c:9:
#7 82.63 Python/marshal.c: In function 'r_object':
#7 82.63 Include/pymem.h:97:30: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#7 82.63    97 |  ( (type *) PyMem_MALLOC((n) * sizeof(type)) ) )
#7 82.63       |                              ^
#7 82.63 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#7 82.63    75 |     : malloc((n) ? (n) : 1))
#7 82.63       |               ^
#7 82.63 Python/marshal.c:874:18: note: in expansion of macro 'PyMem_NEW'
#7 82.63   874 |         buffer = PyMem_NEW(char, n);
#7 82.63       |                  ^~~~~~~~~
#7 82.73 Python/marshal.c: In function 'r_byte':
#7 82.73 Python/marshal.c:528:15: warning: 'ch' may be used uninitialized in this function [-Wmaybe-uninitialized]
#7 82.73   528 |             c = ch;
#7 82.73       |             ~~^~~~
#7 83.13 Python/marshal.c: In function 'PyMarshal_WriteLongToFile':
#7 83.13 Python/marshal.c:72:35: warning: 'wf.ptr' may be used uninitialized in this function [-Wmaybe-uninitialized]
#7 83.13    72 |                       else if ((p)->ptr != (p)->end) *(p)->ptr++ = (c); \
#7 83.13       |                                   ^~
#7 83.13 Python/marshal.c:72:47: warning: 'wf.end' may be used uninitialized in this function [-Wmaybe-uninitialized]
#7 83.13    72 |                       else if ((p)->ptr != (p)->end) *(p)->ptr++ = (c); \
#7 83.13       |                                               ^~
#7 83.13 Python/marshal.c:79:10: warning: 'wf.str' may be used uninitialized in this function [-Wmaybe-uninitialized]
#7 83.13    79 |     if (p->str == NULL)
#7 83.13       |         ~^~~~~
#7 83.24 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/modsupport.o Python/modsupport.c
#7 83.53 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/mystrtoul.o Python/mystrtoul.c
#7 83.68 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/mysnprintf.o Python/mysnprintf.c
#7 83.77 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/peephole.o Python/peephole.c
#7 84.19 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/pyarena.o Python/pyarena.c
#7 84.31 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/pyctype.o Python/pyctype.c
#7 84.40 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/pyfpe.o Python/pyfpe.c
#7 84.42 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/pymath.o Python/pymath.c
#7 84.51 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/pystate.o Python/pystate.c
#7 84.79 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/pythonrun.o Python/pythonrun.c
#7 85.70 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/pytime.o Python/pytime.c
#7 85.77 Python/pytime.c: In function 'pygettimeofday':
#7 85.77 Python/pytime.c:80:9: warning: 'ftime' is deprecated [-Wdeprecated-declarations]
#7 85.77    80 |         ftime(&t);
#7 85.77       |         ^~~~~
#7 85.77 In file included from Python/pytime.c:17:
#7 85.77 /usr/include/x86_64-linux-gnu/sys/timeb.h:39:12: note: declared here
#7 85.77    39 | extern int ftime (struct timeb *__timebuf)
#7 85.77       |            ^~~~~
#7 85.84 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/random.o Python/random.c
#7 85.97 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/structmember.o Python/structmember.c
#7 86.13 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/symtable.o Python/symtable.c
#7 86.97 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE \
#7 86.97 	-DABIFLAGS='"m"' \
#7 86.97 	-o Python/sysmodule.o ./Python/sysmodule.c
#7 87.50 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/traceback.o Python/traceback.c
#7 87.86 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/getopt.o Python/getopt.c
#7 87.96 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/pystrcmp.o Python/pystrcmp.c
#7 88.07 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/pystrtod.o Python/pystrtod.c
#7 88.14 Python/pystrtod.c: In function 'format_float_short':
#7 88.14 Python/pystrtod.c:995:13: warning: 'strncpy' output truncated before terminating nul copying 3 bytes from a string of the same length [-Wstringop-truncation]
#7 88.14   995 |             strncpy(p, "ERR", 3);
#7 88.14       |             ^~~~~~~~~~~~~~~~~~~~
#7 88.25 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/dtoa.o Python/dtoa.c
#7 89.46 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/formatter_unicode.o Python/formatter_unicode.c
#7 90.07 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/fileutils.o Python/fileutils.c
#7 90.30 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE \
#7 90.30 	-DSOABI='"cpython-33m"' \
#7 90.30 	-o Python/dynload_shlib.o ./Python/dynload_shlib.c
#7 90.41 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/thread.o Python/thread.c
#7 90.59 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Modules/config.o Modules/config.c
#7 90.67 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -DPYTHONPATH='":plat-linux"' \
#7 90.67 	-DPREFIX='"/usr/local"' \
#7 90.67 	-DEXEC_PREFIX='"/usr/local"' \
#7 90.67 	-DVERSION='"3.3"' \
#7 90.67 	-DVPATH='""' \
#7 90.67 	-o Modules/getpath.o ./Modules/getpath.c
#7 90.98 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Modules/main.o Modules/main.c
#7 91.22 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Modules/gcmodule.o Modules/gcmodule.c
#7 91.67 gcc -pthread -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/_threadmodule.c -o Modules/_threadmodule.o
#7 91.99 gcc -pthread -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/signalmodule.c -o Modules/signalmodule.o
#7 92.38 gcc -pthread -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/posixmodule.c -o Modules/posixmodule.o
#7 92.49 In file included from Include/Python.h:66,
#7 92.49                  from ./Modules/posixmodule.c:28:
#7 92.49 ./Modules/posixmodule.c: In function 'parse_envlist':
#7 92.49 Include/pymem.h:97:30: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#7 92.49    97 |  ( (type *) PyMem_MALLOC((n) * sizeof(type)) ) )
#7 92.49       |                              ^
#7 92.49 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#7 92.49    75 |     : malloc((n) ? (n) : 1))
#7 92.49       |               ^
#7 92.49 ./Modules/posixmodule.c:4986:15: note: in expansion of macro 'PyMem_NEW'
#7 92.49  4986 |     envlist = PyMem_NEW(char *, i + 1);
#7 92.49       |               ^~~~~~~~~
#7 92.49 Include/pymem.h:97:30: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#7 92.49    97 |  ( (type *) PyMem_MALLOC((n) * sizeof(type)) ) )
#7 92.49       |                              ^
#7 92.49 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#7 92.49    75 |     : malloc((n) ? (n) : 1))
#7 92.49       |               ^
#7 92.49 ./Modules/posixmodule.c:5023:13: note: in expansion of macro 'PyMem_NEW'
#7 92.49  5023 |         p = PyMem_NEW(char, len);
#7 92.49       |             ^~~~~~~~~
#7 92.49 ./Modules/posixmodule.c: In function 'parse_arglist':
#7 92.49 Include/pymem.h:97:30: warning: '*' in boolean context, suggest '&&' instead [-Wint-in-bool-context]
#7 92.49    97 |  ( (type *) PyMem_MALLOC((n) * sizeof(type)) ) )
#7 92.49       |                              ^
#7 92.49 Include/pymem.h:75:15: note: in definition of macro 'PyMem_MALLOC'
#7 92.49    75 |     : malloc((n) ? (n) : 1))
#7 92.49       |               ^
#7 92.49 ./Modules/posixmodule.c:5058:23: note: in expansion of macro 'PyMem_NEW'
#7 92.49  5058 |     char **argvlist = PyMem_NEW(char *, *argc+1);
#7 92.49       |                       ^~~~~~~~~
#7 94.32 gcc -pthread -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/errnomodule.c -o Modules/errnomodule.o
#7 94.46 gcc -pthread -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/pwdmodule.c -o Modules/pwdmodule.o
#7 94.59 gcc -pthread -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/_sre.c -o Modules/_sre.o
#7 97.92 gcc -pthread -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/_codecsmodule.c -o Modules/_codecsmodule.o
#7 98.36 gcc -pthread -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/_weakref.c -o Modules/_weakref.o
#7 98.47 gcc -pthread -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/_functoolsmodule.c -o Modules/_functoolsmodule.o
#7 98.70 gcc -pthread -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/operator.c -o Modules/operator.o
#7 99.13 gcc -pthread -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/_collectionsmodule.c -o Modules/_collectionsmodule.o
#7 99.76 gcc -pthread -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/itertoolsmodule.c -o Modules/itertoolsmodule.o
#7 101.0 gcc -pthread -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/_localemodule.c -o Modules/_localemodule.o
#7 101.2 gcc -pthread -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -I./Modules/_io -c ./Modules/_io/_iomodule.c -o Modules/_iomodule.o
#7 101.5 gcc -pthread -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -I./Modules/_io -c ./Modules/_io/iobase.c -o Modules/iobase.o
#7 101.8 gcc -pthread -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -I./Modules/_io -c ./Modules/_io/fileio.c -o Modules/fileio.o
#7 102.1 gcc -pthread -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -I./Modules/_io -c ./Modules/_io/bytesio.c -o Modules/bytesio.o
#7 102.5 gcc -pthread -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -I./Modules/_io -c ./Modules/_io/bufferedio.c -o Modules/bufferedio.o
#7 103.3 gcc -pthread -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -I./Modules/_io -c ./Modules/_io/textio.c -o Modules/textio.o
#7 104.3 gcc -pthread -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -I./Modules/_io -c ./Modules/_io/stringio.c -o Modules/stringio.o
#7 104.7 gcc -pthread -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/zipimport.c -o Modules/zipimport.o
#7 105.2 gcc -pthread -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/faulthandler.c -o Modules/faulthandler.o
#7 105.4 ./Modules/faulthandler.c: In function 'stack_overflow.constprop':
#7 105.4 cc1: warning: function returns address of local variable [-Wreturn-local-addr]
#7 105.4 ./Modules/faulthandler.c:903:19: note: declared here
#7 105.4   903 |     unsigned char buffer[4096];
#7 105.4       |                   ^~~~~~
#7 105.4 ./Modules/faulthandler.c: In function 'faulthandler_stack_overflow':
#7 105.4 ./Modules/faulthandler.c:920:30: warning: array subscript -13107200 is outside array bounds of 'size_t[1]' {aka 'long unsigned int[1]'} [-Warray-bounds]
#7 105.4   920 |     stop = stack_overflow(sp - STACK_OVERFLOW_MAX_SIZE,
#7 105.4       |                              ^
#7 105.4 ./Modules/faulthandler.c:916:12: note: while referencing 'depth'
#7 105.4   916 |     size_t depth, size;
#7 105.4       |            ^~~~~
#7 105.4 ./Modules/faulthandler.c:921:30: warning: array subscript 13107200 is outside array bounds of 'size_t[1]' {aka 'long unsigned int[1]'} [-Warray-bounds]
#7 105.4   921 |                           sp + STACK_OVERFLOW_MAX_SIZE,
#7 105.4       |                              ^
#7 105.4 ./Modules/faulthandler.c:916:12: note: while referencing 'depth'
#7 105.4   916 |     size_t depth, size;
#7 105.4       |            ^~~~~
#7 105.5 gcc -pthread -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/symtablemodule.c -o Modules/symtablemodule.o
#7 105.6 gcc -pthread -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE  -c ./Modules/xxsubtype.c -o Modules/xxsubtype.o
#7 105.8 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE \
#7 105.8       -DHGVERSION="\"`LC_ALL=C `\"" \
#7 105.8       -DHGTAG="\"`LC_ALL=C `\"" \
#7 105.8       -DHGBRANCH="\"`LC_ALL=C `\"" \
#7 105.8       -o Modules/getbuildinfo.o ./Modules/getbuildinfo.c
#7 105.9 gcc -pthread -c -Wno-unused-result -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes     -I. -IInclude -I./Include    -DPy_BUILD_CORE -o Python/frozen.o Python/frozen.c
#7 106.0 rm -f libpython3.3m.a
#7 106.0 ar rc libpython3.3m.a Modules/getbuildinfo.o
#7 106.0 ar rc libpython3.3m.a Parser/acceler.o Parser/grammar1.o Parser/listnode.o Parser/node.o Parser/parser.o Parser/bitset.o Parser/metagrammar.o Parser/firstsets.o Parser/grammar.o Parser/pgen.o Parser/myreadline.o Parser/parsetok.o Parser/tokenizer.o
#7 106.0 ar rc libpython3.3m.a Objects/abstract.o Objects/accu.o Objects/boolobject.o Objects/bytes_methods.o Objects/bytearrayobject.o Objects/bytesobject.o Objects/cellobject.o Objects/classobject.o Objects/codeobject.o Objects/complexobject.o Objects/descrobject.o Objects/enumobject.o Objects/exceptions.o Objects/genobject.o Objects/fileobject.o Objects/floatobject.o Objects/frameobject.o Objects/funcobject.o Objects/iterobject.o Objects/listobject.o Objects/longobject.o Objects/dictobject.o Objects/memoryobject.o Objects/methodobject.o Objects/moduleobject.o Objects/namespaceobject.o Objects/object.o Objects/obmalloc.o Objects/capsule.o Objects/rangeobject.o Objects/setobject.o Objects/sliceobject.o Objects/structseq.o Objects/tupleobject.o Objects/typeobject.o Objects/unicodeobject.o Objects/unicodectype.o Objects/weakrefobject.o
#7 106.1 ar rc libpython3.3m.a Python/_warnings.o Python/Python-ast.o Python/asdl.o Python/ast.o Python/bltinmodule.o Python/ceval.o Python/compile.o Python/codecs.o Python/dynamic_annotations.o Python/errors.o Python/frozenmain.o Python/future.o Python/getargs.o Python/getcompiler.o Python/getcopyright.o Python/getplatform.o Python/getversion.o Python/graminit.o Python/import.o Python/importdl.o Python/marshal.o Python/modsupport.o Python/mystrtoul.o Python/mysnprintf.o Python/peephole.o Python/pyarena.o Python/pyctype.o Python/pyfpe.o Python/pymath.o Python/pystate.o Python/pythonrun.o Python/pytime.o Python/random.o Python/structmember.o Python/symtable.o Python/sysmodule.o Python/traceback.o Python/getopt.o Python/pystrcmp.o Python/pystrtod.o Python/dtoa.o Python/formatter_unicode.o Python/fileutils.o Python/dynload_shlib.o   Python/thread.o Python/frozen.o
#7 106.1 ar rc libpython3.3m.a Modules/config.o Modules/getpath.o Modules/main.o Modules/gcmodule.o
#7 106.2 ar rc libpython3.3m.a Modules/_threadmodule.o  Modules/signalmodule.o  Modules/posixmodule.o  Modules/errnomodule.o  Modules/pwdmodule.o  Modules/_sre.o  Modules/_codecsmodule.o  Modules/_weakref.o  Modules/_functoolsmodule.o  Modules/operator.o  Modules/_collectionsmodule.o  Modules/itertoolsmodule.o  Modules/_localemodule.o  Modules/_iomodule.o Modules/iobase.o Modules/fileio.o Modules/bytesio.o Modules/bufferedio.o Modules/textio.o Modules/stringio.o  Modules/zipimport.o  Modules/faulthandler.o  Modules/symtablemodule.o  Modules/xxsubtype.o
#7 106.2 ranlib libpython3.3m.a
#7 106.3 gcc -pthread   -Xlinker -export-dynamic -o python Modules/python.o libpython3.3m.a -lpthread -ldl  -lutil   -lm
#7 106.5 ./python -E -S -m sysconfig --generate-posix-vars
#7 106.5 make: *** [Makefile:502: pybuilddir.txt] Segmentation fault
------
executor failed running [/bin/sh -c curl -SL https://www.python.org/ftp/python/3.3.7/Python-3.3.7.tgz | tar -xzvf -     && cd Python-3.3.7 && ./configure && make && make altinstall]: exit code: 2
[+] Building 193.4s (9/9) FINISHED
</pre>

</details>
