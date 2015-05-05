#!/usr/bin/python

import time

import conz


cn = conz.Console(verbose=True)

# Classic success
with cn.progress('Waiting'):
    time.sleep(1)

# Classic failure
with cn.progress('Failing', reraise=False):
    time.sleep(1)
    raise RuntimeError('This is a gratuitous error')

# Classic progress
with cn.progress('Progressing') as p:
    for i in range(10):
        time.sleep(0.2)
        p.prog()

# Multi-step
try:
    with cn.progress('Step 1'):
        time.sleep(1)

    with cn.progress('Step 2'):
        time.sleep(1)

    with cn.progress('Step 3'):
        time.sleep(1)
        raise RuntimeError('Intentional failure')

    with cn.progress('Step 4'):
        time.sleep(1)

except cn.ProgressAbrt:
    cn.perr('Something went wrong during one of the steps')
