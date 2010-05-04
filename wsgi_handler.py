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
import sys, os
DIRNAME = os.path.abspath(os.path.dirname(__file__).decode('utf-8'))
sys.path = [DIRNAME+"/..",DIRNAME] + sys.path

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
       
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

