#!/usr/bin/python

import conz

cn = conz.Console()

show = lambda x: cn.pstd('Got value: {!r} ({})'.format(x, type(x)))
note = lambda x: cn.pstd(cn.color.cyan(x))

# Very basic reading
note('All values will be returned as strings')
val = cn.read('Enter a number:')
show(val)

# Input with clean
note('With cleaner, values are converted to int')
val = cn.read('Enter a number:', clean=conz.safeint)
show(val)

# Using RVPL
note('Again with cleaner but using RVPL.')
note('This example should be the same as previous one')
val = cn.rvpl('Enter a number:', clean=conz.safeint)
show(val)

# Using RVPL with validator
note('This time, we use a validator to make sure we get valid input')
val = cn.rvpl('Enter a number greater than 12:', clean=conz.safeint,
              validator=lambda x: x > 12)
show(val)

# Using RVPL without strict
note('We again use a valiator, but we also provide a default')
val = cn.rvpl('Enter a number greater than 12 [15]:', clean=conz.safeint,
              validator=lambda x: x > 12, strict=False, default=15)
show(val)

# With intro
val = cn.rvpl('Enter some value:', intro='This is the intro text. It is '
              'line-wrapped at terminal width.')
show(val)

# With yesno
val = cn.yesno('Yes or no?')
show(val)

# Yesno with Yes as default
val = cn.yesno('Yes or no?', default=True)
show(val)

# Yesno with No as default
val = cn.yesno('Yes or no?', default=False)
show(val)

# Yesno with intro
val = cn.yesno('Yes or no?', intro='You always liked command line.')
show(val)
