from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'number_playground.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^number-playground/', 'playground.views.playground'),
    url(r'^qikinumber$',        'playground.views.qikinumber'),
)
