from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
# from django.contrib.auth import views as auth_views

urlpatterns = patterns('',
    # url(r'^$', 'number_playground.views.home', name='home'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^number-playground/', 'playground.views.number_playground'),
    url(r'^qikinumber$',        'playground.views.qikinumber'),   # ajax
    url(r'^qiki-playground/',   'playground.views.qiki_playground'),
    url(r'^qiki-ajax$',         'playground.views.qiki_ajax'),

    # url(r'^accounts/login/$', auth_views.login, name='login'),
    # url(r'^accounts/logout/$', auth_views.logout),
    # url('', include('social.apps.django_app.urls', namespace='social')),

    url(r'^accounts/', include('allauth.urls')),
) # + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
