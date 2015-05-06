"""
Class for working with progress context

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from . import ansi_colors


class ProgressEnd(Exception):
    pass


class ProgressOK(ProgressEnd):
    pass


class ProgressAbrt(ProgressEnd):
    pass


class Progress:
    """
    Wrapper that manages step progress
    """

    color = ansi_colors.color

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


