====
conz
====

This module contains a lightweight library for creating command line programs,
conz.

conz has following features:

- Manages signals (SIGINT and SIGPIPE)
- Simplifies working with pipes
- Supports output colorization
- Provides tools for working with long-running tasks
- Controls output in interactive and non-interactive scenarios

.. contents::

Installing
==========

You can install conz from PyPI using pip or easy_install::

    pip install conz

    easy_install conz

Quick tour
==========

A quick tour example can be found in ``examples/quicktour.py``::

    import conz

    someval = True

    cn = conz.Console(verbose=True)

    cn.pstd('This goes to STDOUT')
    cn.perr('This goes to STDERR')
    cn.pverr(someval, 'This message is related to somevar')

    cn.pstd(cn.color.green('This message is green'))

    with cn.progress('Some long operation'):
        import time
        time.sleep(2)

    data = cn.read('Type something in:')
    cn.pstd('You typed in {}'.format(cn.color.yellow(data, style='italic')))

Formatting conventions
======================

Because this library deals with terminal output a lot, we have to somehow tell
when something is terminal output and when it is code. Because of this, we use
lines to delimit console output. For example::

    ----------------------------------------------
    I'm a sample output
    ----------------------------------------------

When output is to the STDERR, 'E' will be shown in the right corner.::
 
    ---------------------------------------------E
    I'm a sample error
    ----------------------------------------------

When user enters data, the Entered data will be followed by ``<Enter>`` and the
right corner will include the 'I' character (for 'interactive session')::

    ---------------------------------------------I
    Prompt: some data<Enter>
    ----------------------------------------------

When value is returned from user input, the value is printed right below the
output preceeded by ``==>``::

    ---------------------------------------------I
    Prompt: some data<Enter>
    ----------------------------------------------
    ==> 'some data'

Usage
=====

The ``conz`` package includes a class ``Console`` which is the only class you
will even need to work with. Simply import and instantiate it at the top of
your program. ::

    import conz
    cn = conz.Console()

Working with output
-------------------

The ``Console()`` class is, for the most part, a wrapper around the ``print()``
function (not print statement, so not compatible with versions of Python that
do not support this). It controls how ``print()`` is invoked and takes care of
some of the edge cases where it may malfunction.

The ``print()`` method on a ``Console`` object is a very simple wrapper around
Python's ``print()`` whic does nothing except pass it's positional and keywrod
arguments to the ``print()`` function. We will never use it directly, though,
as there are shortcuts for doing specific things with ``print()``.

To output to STDOUT, we use the ``pstd()`` method. It takes the same arguments
as ``print()`` function, with the exception of ``file`` keyword argument which
is set by this method and cannot be overridden. ::

    cn.pstd('This always goes to STDOUT', end='...')
    ----------------------------------------------
    This always goes to STDOUT
    ----------------------------------------------

To output to STDERR, we use the ``perr()`` method. As with ``pstd()``, it
overrides the ``file`` argument for us. ::

    cn.perr('Mayday, mayday!')
    ---------------------------------------------E
    Mayday, mayday!
    ----------------------------------------------

The main difference between regular ``print()`` and ``pstd()``/``perr()``
methods is that the latter will flush the STDOUT/STDERR after writing to it.
This can prvent weird issues in some edge cases.

There is a variant of ``perr()`` which prints a more structured message to
STDERR. The ``pverr()`` method takes a value and a message, and prints then in
``VALUE: Message`` format. ::

    path = '/foo/bar/baz.txt'
    cn.verr(path, 'not found')
    ---------------------------------------------E
    /foo/bar/baz.txt: not found
    ----------------------------------------------

A variant of ``pstd()`` is ``pverb()``. It is exactly the same as ``pstd()``,
except that it only outputs when ``verbose`` flag on the ``Console`` object is
``True``. This is useful for programs that need to differentiate between
interactive and non-interactive use (e.g., using in pipe vs invoking directly)
or wish to have a ``--verbose`` switch, etc. ::

    cn.verbose = True
    cn.pverb("I'm a talkative program")
    ----------------------------------------------
    I'm a talkative program
    ----------------------------------------------

    cn.verbose = False
    cn.pverb("I'm a talkative program")
    ----------------------------------------------

    ----------------------------------------------

The ``verbose`` flag can be set either as an argument during instantiation, or
simply by setting the attribute as in the previous example.

The ``Console`` object also provides a ``outterm`` property which is ``False``
when program is outputting to a pipe rather than the terminal::

    if cn.outterm:
        # give full output to the user
    else:
        # give a short output that can be parsed by a machine, etc

Colorizing
----------

Before we start, note that this implementation is **not cross-platform**. If
you need something with a bit more punch, you should look at colorama_.

To colorize the output, both the ``conz`` module and ``Console`` class have a 
``color`` attribute, which provides methods for output colorization. Each piece
of text can have the following attributes:

- foreground color
- style
- background color

Foreground and background colors can be:

- black
- red
- green
- yellow
- blue
- purple (magenta)
- cyan
- white

Styles can be:

- bold
- italic
- underline
- blink
- reverse (inverts foreground and background colors)

Each of these colors have a method on the ``color`` attribute. Each color
method takes ``style`` and ``bg`` keyword arguments which set the style and
background color respectively. The ``color()`` method can be used to specify
colors dynamically. Here are some examples::

    cn.color.red('This is red text')
    cn.color.color('This is red text', color='red')
    cn.color.blue('This is blue underlined text', style='underline')
    cn.color.color('This is green on yellow', color='green', bg='yellow')

You can find an example script in ``examples/colors.py`` which prings all
possible combinations of various colors, styles, and backgrounds.

Working with input
------------------

There are two types of input you can work with: interactive user input, and 
pipes.

To read the user input, use ``read()`` method. This method takes two optional 
arguments. One is the ``prompt`` argument, which we use to set the prompt. It
is an empty string by default. The other argument is a data-cleaning function.
When you pass the ``clean`` argument, user input is passed through the function
before it is retuned. For example::

    cn.read('Exit? [y/N] ', clean=lambda x: x.lower()[:1] == 'y')
    ---------------------------------------------I
    Exit? [y/N] y<Enter>
    ----------------------------------------------
    ==> True

Note that this method uses ``raw_input()`` on Python 2.7.x and ``input()`` on
Python 3.x.

To work with pipes, we use the ``readpipe()`` method. This method reads from
the STDIN pipe one line at a time and returns an iterator that allows us to
iterate over the lines. ::

    for l in cn.readpipe():
        l = l.strip()
        cn.pstd('Received: {}'.format())

Note that line-feed characters are not stripped from the output so it is up to
us to strip it away.

When working with a large number of lines coming down the pipe, we may
sometimes need to work in batches, rather than one line at a time. The
``chunk`` argument can be set to an integer value that specifies the number of
lines we want buffered before they are returned to us. When using chunks, the
lines are returned as a list of strings, rather than strings. The following
example will return pipe input in groups of 500::

    for lines in cn.readpipe(500):
        # do something with 500 lines

If we need to know whether input will come from a pipe or not, we can use the
``interm`` property. ::

    if cn.interm:
        # possibly interactive version
    else:
        # we are on the receiving end of a pipe

Advanced interactive input
--------------------------

So far we have looked at simpe user input. However in most cases, input is not
the only thing we want. We normally also need to show notes, validate the
input, construct menus, etc. The ``Console`` class provides three methods that
are useful for different scenarios.

You will find examples of code discussed here in ``examples/user_input.py`` and
``examples/menu.py``.

RVPL
~~~~

RVPL (pead validate print loop) is a loop in which some data is read from the
user, validated, and error message printed. This loop continues as long as data
is invalid. The ``rvpl()`` method is used to start such a loop.

At bare minimum, ``rvpl()`` is called with a prompt that should be shown to the
user. ::

    cn.rvpl('Please enter your name:')
    ---------------------------------------------I
    Please enter your name: My name<enter>
    ----------------------------------------------
    ==> 'My name'

Like ``read()``, ``rvpl()`` also takes a ``clean`` argument, which is used to
control how the value is cleaned. In addition, it takes ``validator`` argument,
which is a function that validates the cleaned data. The default validator
simply makes sure the input is not an empty string.

For invalid input, error message is displayed::

    cn.rvpl('Please enter your name:')
    ---------------------------------------------I
    Please enter your name: <Enter>
    Entered value is invalid
    Please enter your name: Mike<Enter>
    ----------------------------------------------
    ==> 'Mike'

Error message can be customized using the ``error`` argument. If ``error``
argument is is a callable, it will be called with entered value and it must 
return the message to be shown. ::

    valid_input = ('a', 'b', 'c')
    error = lambda x: '{} is not one of the {}'.format(
        x, ', '.join(valid_input))
    validator = lambda x: x in valid_input
    cn.rvpl('Type one of the first 3 characters of English alphabet:')
    ---------------------------------------------I
    Type one of the first 3 characters of English alphabet: e<Enter>
    e is not one of the a, b, c
    Type one of the first 3 characters of English alphabet: b<Enter>
    ----------------------------------------------
    ==> 'b'

An intro message can be passed which is shown above the prompt. Unlinke the
prompt itself, intro message is not repeated in the loop. ::

    cn.rvpl('>', intro='Please enter your name:')
    ---------------------------------------------I
    Please enter your name: 
    > <Enter>
    Entered value is invalid
    > Mike<Enter>
    ----------------------------------------------
    ==> 'Mike'

When requesting optional input, the strict validation can be turned off using
the ``strict`` argument. When this argument is ``False``, then the loop exists
even when validation fails. The value returned when validation fails is
controlled by ``default`` argument, which defaults to ``None``. ::

    cn.rvpl('Please enter your name:', strict=False, default='Bob')
    ---------------------------------------------I
    Please enter your name: <Enter>
    ----------------------------------------------
    ==> 'Bob'

Yes/No input
~~~~~~~~~~~~

The ``yesno()`` method provides a specialized version the RVPL limited to yes
and no answer, and returnin ``True`` or ``False``. ::

    cn.yesno('Are you all right?')
    ---------------------------------------------I
    Are you all right? (y/n): y<Enter>
    ----------------------------------------------
    ==> True

The prompt passed to ``yesno()`` is automatically appended the '(y/n):' string.
The appearance of this string depends on the default value discussed further
below.

Since it is a wrapper around ``rvpl()`` it takes the same ``error`` and
``intro`` arguments which behave the same way.

Although it takes the ``default`` argument like ``rvpl()``, the behavior is
different. When ``default`` is ``None`` it automatically turns on strict
validation. The argument can also be either ``True`` or ``False``, in which
case the default value is respectively 'yes' and 'no'. ::

    cn.yesno('Are you all right?', default=True)
    ---------------------------------------------I
    Are you all right? (Y/n): <Enter>
    ----------------------------------------------
    ==> True
    
    cn.yesno('Are you all right?', default=False
    ---------------------------------------------I
    Are you all right? (y/N): <Enter>
    ----------------------------------------------
    ==> False

Menu
~~~~

Menu is another specialization of the RVPL, used for displaying menus. This is
facilitated by the ``menu()`` method. 

This method has only one required argument, which is an iterable of menu
choices. Each member of the iterable must be a two-tuple which holds the actual
value as first member and the value's label as second. For example::

    choices = (('f', 'foo'), ('b', 'bar'))
    cn.menu(choices)
    ---------------------------------------------I
      1) foo
      2) bar
    Please choose from the provided options: 1<Enter>
    ----------------------------------------------
    ==> 'f'

Almost all aspects of the menu can be customized. The ``prompt``, ``error``,
``intro``, ``strict`` and ``default`` behave the same way as in regular RVPL so
we will not discuss them in detail here.

Display of the menu items themselves is controlled by two arguments:
``formatter`` and ``numerator``.

``numerator`` argument controls how the enumeration of the menu items is done.
It takes the number of menu items as its only argument, and must return a list
of strings to be used as options. For example::

    choices = (('f', 'foo'), ('b', 'bar'))
    numer = lambda n: ('abcd'[i] for i in range(n), numerator=numer)
    cn.menu(choices)
    ---------------------------------------------I
      a) foo
      b) bar
    Please choose from the provided options: a<Enter>
    ----------------------------------------------
    ==> 'f'

``formatter`` takes the number of the item and item's label and must return a
formatted menu item. For example::

    choices = (('f', 'foo'), ('b', 'bar'))
    fmt = lambda n, lbl: '{} ({})'.format(lbl, n)
    cn.menu(choices, formatter=fmt)
    ---------------------------------------------I
    foo (1)
    bar (2)
    Please choose from the provided options: 1<Enter>
    ----------------------------------------------
    ==> 'f'

Working with progress
---------------------

Progress is a more complex construct that we use to notify user of some
activity that may take a while. Each progress has a start banner, which is
printed before we begin, and two end banners, one for success and one for
failure.

Before we can use the progress context manager, we must enable verbose mode. ::

    cn.verbose = True

A progress is started using the ``progress()`` method, which is a context
manager. ::

    with cn.progress("Let's get this show on the road"):
        # do something

This is the simplest form. When an exception of any kind is triggered inside
the context, it is trapped, the failure banner is printed, and the
``conz.ProgressAbrt`` exception is raised. (This exception is also available as
an attribute on ``Console`` objects for convenience.) If everything goes well,
then the success banner will be printed. With the previous code snippet, sucess
output may look like this::

    ----------------------------------------------
    Let's get this show on the road...DONE
    ----------------------------------------------

And failure would look like this::

    ----------------------------------------------
    Let's get this show on the road...FAIL
    ----------------------------------------------

The end banners can be customized by using the ``end`` and ``abrt`` arguments::

    with cn.progress('Almost there', end='finally!', abrt='awww, bummer'):
        # do something

The outputs would look like this::

    ----------------------------------------------
    Almost there...finally!
    ----------------------------------------------

or::

    ----------------------------------------------
    Almost there...awww, bummer
    ----------------------------------------------

The elipsis (three dots) can be customized using the ``sep`` argument::

    with cn.progress('File check', sep=': '):
        # do something

This results in::

    ----------------------------------------------
    File check: DONE
    ----------------------------------------------

or::

    ----------------------------------------------
    File check: FAIL
    ----------------------------------------------

By default, the progress context manager will trap any exception. This may or
may not make sense for a particular situation. This behavior can therefore be
customized using the ``excs`` argument, which takes a tuple of exception
classes that we are expecting. Passing exceptions explicitly like this allows
the context manager to propagate unhandled exceptions and reval subtle flaws in
our logic.

We can also specify a callback that runs each time an exception (other than
``ProgressAbrt`` and ``ProgressOK`` are raised inside the context. This
callback is specified using ``onerror`` argument, and defaults to an error
handler that prints 'Program error: ERROR MESSAGE' to STDERR. For convenience,
the ``Console`` object has a ``error()`` method which creates such handlers.

To create a handler, we call the ``error()`` method like so::

    handler = cn.error('Ouch!', exit=1)
    with cn.progress('Ouch progress', onerror=handler):
        raise RuntimeError()

The above results in::

    ----------------------------------------------
    Outch progress...FAIL
    Ouch!
    ----------------------------------------------

The message may have a ``{err}`` placeholder, which gets replaced by the string
representation of the exception that was raised in the block.

To completely suppress the error handler, simply pass it a function that does
nothing. ::

    with cn.progress('No ouch', onerror: lambda exc: None):
        raise RuntimeError()
    ----------------------------------------------
    No ouch...FAIL
    ----------------------------------------------

.. note::
    Note that passing ``None`` as ``onerror`` value simply causes the default
    error handler to be used instead.

The progress context manager returns a ``Progress`` object, which provides
methods for explicitly terminating the progress, and printing the progress
indicator. This object has ``end()`` and ``abrt()`` methods, which are called
to terminate with success and error status respectively. For example::

    with cn.progress('Something') as prg:
        if not success:
            prg.abrt()
        prg.end()

The ``end()`` and ``abrt()`` methods raise ``ProgressOK`` and ``ProgressAbrt``
exceptions repsectively. We can suppress raising of the exceptions using
``noraise`` argument and setting it to ``True``. Both of the methods will use
the default end banners. We can also use any banner we want by passing it as
the first positional argument. This can be useful in cases where the end banner
should indicate different outcomes.

.. note::
    Default banners are colorized (green for success, red for failure). Any
    custom banners passed directly to ``end()`` and ``abrt()`` will not be
    colorized, though.

The ``ProgressOK`` exception is not meant to be
handled by us in any way, and it's simply there to facilitate flow control.
``ProgressAbrt`` is, by default, reraised so that code outside the context
manager can handle it. Therefore, we normally wrap the context block in a
try-except::

    try:
        with cn.progress('Something'):
            # do something
    except cn.ProgressAbrt:
        # something went wrong

This reraising of the ``ProgressAbrt`` exception can be suppressed by using the
``reraise`` argument which can be ``True`` or ``False``. Setting this flag to
``False`` silences the ``ProgressAbrt`` exception. At that point, we are still
able to do error handling using the ``onerror`` callback.

You can find a script in ``examples/progress.py`` which demonstrates a few
typical cases.

Quitting
--------

To quit the program, we call the ``quit()`` method on the ``Console`` object.
This method works the same way as ``sys.exit()`` (except that it takes one less
``import`` to use it).

Signal handling
---------------

The default implementation of ``Console`` class automatically takes care of
``SIGINT`` (keyboard interrupt) and ``SIGPIPE`` (broken pipe) signals. You can
customize the way those are handled by overloading the ``onint()`` and
``onpipe()`` methods. You can also customize the registration of signals
themselves by overloading the ``register_signals()`` method.


Reporting bugs
==============

Please report any bugs or feature requests to the `issue tracker`_.

.. _colorama: https://pypi.python.org/pypi/colorama
.. _issue tracker: https://github.com/Outernet-Project/conz/issues
