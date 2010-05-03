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
