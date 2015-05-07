"""
Functions for working with console

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import print_function

import sys
import signal
import traceback
import contextlib

from . import utils
from . import progress
from . import ansi_colors

try:
    read = raw_input
except NameError:
    read = input


class Console:
    """
    Wrapper around print with helper methods that cover typical ``print()``
    usage in console programs.
    """

    ProgressEnd = progress.ProgressEnd
    ProgressOK = progress.ProgressOK
    ProgressAbrt = progress.ProgressAbrt

    color = ansi_colors.color

    def __init__(self, verbose=False, stdout=sys.stdout, stderr=sys.stderr,
                 debug=False):
        """
        ``verbose`` flag controls suppression of verbose outputs (those printed
        using ``pverb()`` method). The verbose output is usually a helpful
        message for interactive applications, but may break other scripts in
        pipes.

        ``stdout`` and ``stderrr`` are the default STDOUT file for all
        ``print()`` calls.

        To enable debugging (e.g., printing stack traces), use the ``debug``
        argument and set it to ``True``.
        """
        self.verbose = verbose
        self.out = stdout
        self.err = stderr
        self.register_signals()
        self.debug = debug

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

    def rvpl(self, prompt, error='Entered value is invalid', intro=None,
             validator=lambda x: x != '', clean=lambda x: x.strip(),
             strict=True, default=None):
        """ Start a read-validate-print loop

        The RVPL will read the user input, validate it, and loop until the
        entered value passes the validation, then return it.

        Error message can be customized using the ``error`` argument. If the
        value is a callable, it will be called with the value and it will be
        expected to return a printable message. Exceptions raised by the
        ``error`` function are not trapped.

        When ``intro`` is passed, it is printed above the prompt.

        The ``validator`` argument is is a function that validates the user
        input. Default validator simply validates if user entered any value.

        The ``clean`` argument specifies a function for the ``read()`` method
        with the same semantics.
        """
        if intro:
            self.pstd(utils.rewrap_long(intro))
        val = self.read(prompt, clean)
        while not validator(val):
            if not strict:
                return default
            if hasattr(error, '__call__'):
                self.perr(error(val))
            else:
                self.perr(error)
            val = self.read(prompt, clean)
        return val

    def yesno(self, prompt, error='Please type either y or n', intro=None,
              default=None):
        """ Ask user for yes or no answer

        The prompt will include a typical '(y/n):' at the end. Depending on
        whether ``default`` was specified, this may also be '(Y/n):' or
        '(y/N):'.

        The ``default`` argument can be ``True`` or ``False``, with meaning of
        'yes' and 'no' respectively. Default is ``None`` which means no
        default. When default value is specified, malformed or empty response
        will cause the ``default`` value to be returned.

        Optional ``intro`` text can be specified which will be shown above the
        prompt.
        """
        if default is None:
            prompt += ' (y/n):'
        else:
            if default is True:
                prompt += ' (Y/n):'
                default = 'y'
            if default is False:
                prompt += ' (y/N):'
                default = 'n'
        validator = lambda x: x in ['y', 'yes', 'n', 'no']
        val = self.rvpl(prompt, error=error, intro=intro, validator=validator,
                        clean=lambda x: x.strip().lower(),
                        strict=default is None, default=default)
        return val in ['y', 'yes']

    def menu(self, choices, prompt='Please choose from the provided options:',
             error='Invalid choice', intro=None, strict=True, default=None,
             numerator=lambda x: [i + 1 for i in range(x)],
             formatter=lambda x, y: '{0:>3}) {1}'.format(x, y),
             clean=utils.safeint):
        """ Print a menu

        The choices must be an iterable of two-tuples where the first value is
        the value of the menu item, and the second is the label for that
        matches the value.

        The menu will be printed with numeric choices. For example::

            1) foo
            2) bar

        Formatting of the number is controlled by the formatter function which
        can be overridden by passing the ``formatter`` argument.

        The numbers used for the menu are generated using the numerator
        function which can be specified using the ``numerator`` function. This
        function must take the number of choices and return the same number of
        items that will be used as choice characters as a list.

        The cleaner function is passed to ``pvpl()`` method can be customized
        using ``clean`` argument. This function should generally be customized
        whenever ``numerator`` is customized, as default cleaner converts
        input to integers to match the default numerator.

        Optional ``intro`` argument can be passed to print a message above the
        menu.

        The return value of this method is the value user has chosen. The
        prompt will keep asking the user for input until a valid choice is
        selected. Each time an invalid selection is made, error message is
        printed. This message can be customized using ``error`` argument.

        If ``strict`` argument is set, then only values in choices are allowed,
        otherwise any value will be allowed. The ``default`` argument can be
        used to define what value is returned in case user select an invalid
        value when strict checking is off.
        """
        numbers = list(numerator(len(choices)))
        labels = (label for _, label in choices)
        values = [value for value, _ in choices]
        # Print intro and menu itself
        if intro:
            self.pstd('\n' + utils.rewrap_long(intro))
        for n, label in zip(numbers, labels):
            self.pstd(formatter(n, label))
        # Define the validator
        validator = lambda x: x in numbers
        val = self.rvpl(prompt, error=error, validator=validator, clean=clean,
                        strict=strict, default=default)
        if not strict and val == default:
            return val
        return values[numbers.index(val)]

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
        program quits after printing the message using its value as return
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
        """ Context manager for handling interactive prog indication

        This context manager streamlines presenting banners and prog
        indicators. To start the prog, pass ``msg`` argument as a start
        message. For example::

            printer = Console(verbose=True)
            with printer.progress('Checking files') as prog:
                # Do some checks
                if errors:
                    prog.abrt()
                prog.end()

        The context manager returns a ``Progress`` instance, which provides
        methods like ``abrt()`` (abort), ``end()`` (end), and ``prog()`` (print
        prog indicator).

        The prog methods like ``abrt()`` and ``end()`` will raise an
        exception that interrupts the prog. These exceptions are
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

        Finally, when prog is aborted either naturally or when exception is
        raised, it is possible to reraise the ``ProgressAbrt`` exception. This
        is done using the ``reraise`` flag. Default is to reraise.
        """
        if not onerror:
            onerror = self.error()
        if type(onerror) is str:
            onerror = self.error(msg=onerror)
        self.pverb(msg, end=sep)
        prog = progress.Progress(self.pverb, end=end, abrt=abrt, prog=prog)
        try:
            yield prog
            prog.end()
        except self.ProgressOK:
            pass
        except self.ProgressAbrt as err:
            if reraise:
                raise err
        except KeyboardInterrupt:
            raise
        except excs as err:
            prog.abrt(noraise=True)
            if onerror:
                onerror(err)
            if self.debug:
                traceback.print_exc()
            if reraise:
                raise self.ProgressAbrt()
