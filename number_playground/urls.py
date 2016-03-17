# from django.conf import settings
from django.conf.urls import include, url
# from django.conf.urls.static import static
from django.contrib import admin
# from django.contrib.auth import views as auth_views

import playground.views
# THANKS:  For fixing this warning, at http://stackoverflow.com/a/34096508/673991
# "RemovedInDjango110Warning: Support for string view arguments to url() is deprecated
#  and will be removed in Django 1.10 (got playground.views.number_playground).
#  Pass the callable instead."

import allauth.urls
# NO THANKS:  For fixing this other warning, at http://stackoverflow.com/q/31474285/673991
# "RemovedInDjango110Warning: django.conf.urls.patterns() is deprecated
#  and will be removed in Django 1.10. Update your urlpatterns to be a list of
#  django.conf.urls.url() instances instead."


urlpatterns = [
    # url(r'^$', 'number_playground.views.home', name='home'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^number-playground/', playground.views.number_playground),
    url(r'^qikinumber$',        playground.views.number_playground_submission),   # ajax
    url(r'^qiki-playground/',   playground.views.qiki_playground),
    url(r'^qiki-ajax$',         playground.views.qiki_ajax),

    # url(r'^accounts/login/$', auth_views.login, name='login'),
    # url(r'^accounts/logout/$', auth_views.logout),
    # url('', include('social.apps.django_app.urls', namespace='social')),

    # url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/', include(allauth.urls)),
] # + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
