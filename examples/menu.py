#!/usr/bin/python

import conz

cn = conz.Console()

choices = (
    ('FO', 'Foo'),
    ('BA', 'Bar'),
    ('BZ', 'Baz'),
    ('FA', 'Fam'),
)

show = lambda v: cn.pstd('Got value {}'.format(val))

# Simple default usage
val = cn.menu(choices)
show(val)

# Custom prompt and intro
val = cn.menu(choices, prompt='Tells us what you want [1-4]: ',
              intro='Once upon a time, there was a menu.')
show(val)

# Custom numbering
numerator = lambda n: ['abcd'[i] for i in range(n)]
clean = lambda x: x.strip()
val = cn.menu(choices, numerator=numerator, clean=clean)
show(val)

# Custom formatter
formatter = lambda i, l: '[{}] {}'.format(i, l)
val = cn.menu(choices, formatter=formatter)
show(val)

# Defaults
val = cn.menu(choices, strict=False, default='FO',
              prompt='Choose an item [1]:')
show(val)
