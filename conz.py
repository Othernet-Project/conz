"""
Functions for working with console

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import print_function

import os
import sys
import signal
import contextlib


__version__ = '0.1.post1'
__author__ = 'Outernet Inc'


try:
    read = raw_input
except NameError:
    read = input


class ProgressEnd(Exception):
    pass


class ProgressOK(ProgressEnd):
    pass


class ProgressAbrt(ProgressEnd):
    pass


class Color:
    COLORS = {
        'black': '30',
        'red': '31',
        'green': '32',
        'yellow': '33',
        'blue': '34',
        'purple': '35',
        'cyan': '36',
        'white': '37',
    }

    BACKGROUNDS = {
        'black': '40',
        'red': '41',
        'green': '42',
        'yellow': '43',
        'blue': '44',
        'purple': '45',
        'cyan': '46',
        'white': '47',
    }

    STYLES = {
        'bold': '1',
        'dim': '2',
        'italic': '3',
        'underline': '4',
        'blink': '5',
        'reverse': '7',
    }

    RESET = 0

    @staticmethod
    def _esc(code):
        isatty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        if sys.platform in ['PocketPC', 'win32'] and not isatty:
            return ''
        if os.getenv('ANSI_COLORS_DISABLED'):
            return ''
        return '\033[{}m'.format(code)

    def _wrap(self, s, codes=[RESET]):
        codes = ''.join(self._esc(c) for c in codes)
        return '{}{}{}'.format(codes, s, self._esc(self.RESET))

    def color(self, s, color='default', style=None, bg=None):
        codes = []
        fg = self.COLORS[color]
        if style:
            fg += ';' + self.STYLES[style]
        codes.append(fg)
        if bg:
            codes.append(self.BACKGROUNDS[bg])
        return self._wrap(s, codes)

    def black(self, s, style=None, bg=None):
        return self.color(s, 'black', style, bg)

    def red(self, s, style=None, bg=None):
        return self.color(s, 'red', style, bg)

    def green(self, s, style=None, bg=None):
        return self.color(s, 'green', style, bg)

    def yellow(self, s, style=None, bg=None):
        return self.color(s, 'yellow', style, bg)

    def blue(self, s, style=None, bg=None):
        return self.color(s, 'blue', style, bg)

    def purple(self, s, style=None, bg=None):
        return self.color(s, 'purple', style, bg)

    def cyan(self, s, style=None, bg=None):
        return self.color(s, 'cyan', style, bg)

    def white(self, s, style=None, bg=None):
        return self.color(s, 'white', style, bg)


color = Color()


class Progress:
    """
    Wrapper that manages step progress
    """

    color = color

    def __init__(self, printer, end='DONE', abrt='FAIL', prog='.'):
        """
        The ``Console`` method to be used is specified using the ``printer``
        argument.

        ``end`` argument specified the progress end banner. It defaults to
        'DONE'.

        The ``abrt`` argument specifies the abort banner, defaulting to 'FAIL'.

        The ``prog`` argument specifies the character to be used as progress
        indicator. It defaults to '.'.

        The methods in this class all print using printer's ``pverb()`` method.
        This can be changed by specifying a different method using the
        ``mthod`` argument.
        """
        self.printer = printer
        self.end_msg = end
        self.prog_msg = prog
        self.abrt_msg = abrt

    def end(self, s=None, post=None, noraise=False):
        """ Prints the end banner and raises ``ProgressOK`` exception

        When ``noraise`` flag is set to ``True``, then the exception is not
        raised, and progress is allowed to continue.

        If ``post`` function is supplied it is invoked with no arguments after
        the close banner is printed, but before exceptions are raised. The
        ``post`` function takes no arguments.
        """
        s = s or self.end_msg
        self.printer(self.color.green(s))
        if post:
            post()
        if noraise:
            return
        raise ProgressOK()

    def abrt(self, s=None, post=None, noraise=False):
        """ Prints the abrt banner and raises ``ProgressAbrt`` exception

        When ``noraise`` flag is set to ``True``, then the exception is not
        raised, and progress is allowed to continue.

        If ``post`` function is supplied it is invoked with no arguments after
        the close banner is printed, but before exceptions are raised. The
        ``post`` function takes no arguments.
        """
        s = s or self.abrt_msg
        self.printer(self.color.red(s))
        if post:
            post()
        if noraise:
            return
        raise ProgressAbrt()

    def prog(self, s=None):
        """ Prints the progress indicator """
        s = s or self.prog_msg
        self.printer(s, end='')


class Console:
    """
    Wrapper around print with helper methods that cover typical ``print()``
    usage in console programs.
    """

    ProgressEnd = ProgressEnd
    ProgressOK = ProgressOK
    ProgressAbrt = ProgressAbrt

    color = color

    def __init__(self, verbose=False, stdout=sys.stdout, stderr=sys.stderr):
        """
        ``verbose`` flag controls suppression of verbose outputs (those printed
        using ``pverb()`` method). The verbose output is usually a helpful
        message for interactive applications, but may break other scripts in
        pipes.

        ``stdout`` and ``stderrr`` are the default STDOUT file for all
        ``print()`` calls.
        """
        self.verbose = verbose
        self.out = stdout
        self.err = stderr
        self.register_signals()

    def print(self, *args, **kwargs):
        """ Thin wrapper around print

        All other methods must go through this method for all printing needs.
        """
        print(*args, **kwargs)

    def pstd(self, *args, **kwargs):
        """ Console to STDOUT """
        kwargs['file'] = self.out
        self.print(*args, **kwargs)
        sys.stdout.flush()

    def perr(self, *args, **kwargs):
        """ Console to STERR """
        kwargs['file'] = self.err
        self.print(*args, **kwargs)
        sys.stderr.flush()

    def pverr(self, val, msg, *args, **kwargs):
        kwargs.setdefault('file', self.err)
        self.print('{}: {}'.format(val, msg), *args, **kwargs)

    def pverb(self, *args, **kwargs):
        """ Console verbose message to STDOUT """
        if not self.verbose:
            return
        self.pstd(*args, **kwargs)

    def quit(self, code=0):
        sys.exit(code)

    def read(self, prompt='', clean=lambda x: x):
        """ Display a prompt and ask user for input

        A function to clean the user input can be passed as ``clean`` argument.
        This function takes a single value, which is the string user entered,
        and returns a cleaned value. Default is a pass-through function, which
        is an equivalent of::

            def clean(val):
                return val
        """
        ans = read(prompt + ' ')
        return clean(ans)

    def readpipe(self, chunk=None):
        """ Return iterator that iterates over STDIN line by line

        If ``chunk`` is set to a positive non-zero integer value, then the
        reads are performed in chunks of that many lines, and returned as a
        list. Otherwise the lines are returned one by one.
        """
        read = []
        while True:
            l = sys.stdin.readline()
            if not l:
                if read:
                    yield read
                    return
                return
            if not chunk:
                yield l
            else:
                read.append(l)
                if len(read) == chunk:
                    yield read

    @property
    def interm(self):
        return hasattr(sys.stdin, 'isatty') and sys.stdin.isatty()

    @property
    def outterm(self):
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

    def register_signals(self):
        signal.signal(signal.SIGINT, self.onint)
        signal.signal(signal.SIGPIPE, self.onpipe)

    def onint(self, signum, exc):
        self.perr('\nQuitting program due to keyboard interrupt')
        self.quit(1)

    def onpipe(self, signup, exc):
        self.quit(1)

    def error(self, msg='Program error: {err}', exit=None):
        """ Error handler factory

        This function takes a message with optional ``{err}`` placeholder and
        returns a function that takes an exception object, prints the error
        message to STDERR and optionally quits.

        If no message is supplied (e.g., passing ``None`` or ``False`` or empty
        string), then nothing is output to STDERR.

        The ``exit`` argument can be set to a non-zero value, in which case the
        propgram quits after printing the message using its value as return
        value of the program.

        The returned function can be used with the ``progress()`` context
        manager as error handler.
        """
        def handler(exc):
            if msg:
                self.perr(msg.format(err=exc))
            if exit is not None:
                self.quit(exit)
        return handler

    @contextlib.contextmanager
    def progress(self, msg, onerror=None, sep='...', end='DONE', abrt='FAIL',
                 prog='.', excs=(Exception,), reraise=True):
        """ Context manager for handling interactive progress indication

        This context manager streamlines presenting banners and progress
        indicators. To start the progress, pass ``msg`` argument as a start
        message. For example::

            printer = Console(verbose=True)
            with printer.progress('Checking files') as progress:
                # Do some checks
                if errors:
                    progress.abrt()
                progress.end()

        The context manager returns a ``Progress`` instance, which provides
        methods like ``abrt()`` (abort), ``end()`` (end), and ``prog()`` (print
        progress indicator).

        The progress methods like ``abrt()`` and ``end()`` will raise an
        exception that interrupts the progress. These exceptions are
        ``ProgressEnd`` exception subclasses and are ``ProgressAbrt`` and
        ``ProgressOK`` respectively. They are silenced and not handled in any
        way as they only serve the purpose of flow control.

        Other exceptions are trapped and ``abrt()`` is called. The exceptions
        that should be trapped can be customized using the ``excs`` argument,
        which should be a tuple of exception classes.

        If a handler function is passed using ``onerror`` argument, then this
        function takes the raised exception and handles it. By default, the
        ``error()`` factory is called with no arguments to generate the default
        error handler. If string is passed, then ``error()`` factory is called
        with that string.

        Finally, when progress is aborted either naturally or when exception is
        raised, it is possible to reraise the ``ProgressAbrt`` exception. This
        is done using the ``reraise`` flag. Default is to reraise.
        """
        if not onerror:
            onerror = self.error()
        if type(onerror) is str:
            onerror = self.error(msg=onerror)
        self.pverb(msg, end=sep)
        progress = Progress(self.pverb, end=end, abrt=abrt, prog=prog)
        try:
            yield progress
            progress.end()
        except ProgressOK:
            pass
        except ProgressAbrt as err:
            if reraise:
                raise err
        except KeyboardInterrupt:
            raise
        except excs as err:
            progress.abrt(noraise=True)
            if onerror:
                onerror(err)
            if reraise:
                raise ProgressAbrt()
