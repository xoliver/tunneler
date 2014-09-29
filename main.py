#!env python

import sys

from tunneler.tunneler import Tunneler
from tunneler.processhelper import ProcessHelper

if __name__ == '__main__':
    tunneler = Tunneler(ProcessHelper())
    tunneler.execute(sys.argv[1], sys.argv[2:])
