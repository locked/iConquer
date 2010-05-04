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
from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings


admin.autodiscover()

urlpatterns = patterns('',
	(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
	#(r'^media-admin/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
	(r'^[a-z]*$', 'rts.views.menu'),
	(r'^(?P<gameid>[0-9]+)$', 'rts.views.game'),
	(r'^get_all_obj_tiles$', 'rts.views.get_all_obj_tiles'),
	(r'^get_ground/(?P<gameid>.*)$', 'rts.views.get_ground'),
	(r'^accounts/', include('registration.backends.default.urls')),
	(r'^admin/', include(admin.site.urls)),
	#url(r'^', include('socialregistration.urls')),
)
