#!/usr/bin/python

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
