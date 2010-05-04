'''
 * iConquer - Online C&C-like game
 * Copyright (C) 2009-2010 Adam Etienne <etienne.adam@gmail.com>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation version 3.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * $Id$
'''
"""fnl.core.memory module

Trivial, but working code to get the memory usage of the current process
where the pid is retrieved using os.getpid() and the memory usage is read
from the unix command ps.    
"""

import os

__version__ = "1.0"
__author__ = "Florian Leitner"

def mem(size="rss"):
    """Generalization; memory sizes: rss, rsz, vsz."""
    return int(os.popen('ps -p %d -o %s | tail -1' %
                        (os.getpid(), size)).read())

def rss():
    """Return ps -o rss (resident) memory in kB."""
    return mem("rss")

def rsz():
    """Return ps -o rsz (resident + text) memory in kB."""
    return mem("rsz")

def vsz():
    """Return ps -o vsz (virtual) memory in kB."""
    return mem("vsz")
