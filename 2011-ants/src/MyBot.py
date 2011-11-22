#!/usr/bin/env python
from random import shuffle
from ants import *
from EskymoBot import *
from Strategy import *

if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    try:
        strategy = Strategy()
        strategy.run(EskymoBot(), AntsDriver())
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
