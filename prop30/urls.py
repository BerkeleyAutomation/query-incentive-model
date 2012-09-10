from django.conf.urls.defaults import *
import os

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^prop30/', include('prop30.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
	(r'^bootstrap/(?P<path>.*)$', 'django.views.static.serve',{'document_root': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bootstrap').replace('\\','/')}),
    (r'^score/(\w+)', 'prop30.views.data'),
    (r'^about/$', 'prop30.views.about'),
    (r'^save/(\w+)', 'prop30.views.save'),
    (r'^save/$', 'prop30.views.save'),
    (r'^$', 'prop30.views.index'),
    (r'^(\w+)', 'prop30.views.index'),
)
