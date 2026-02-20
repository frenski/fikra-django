"""fikra URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.conf import settings
from django.views.static import serve as django_static_serve
from django.contrib.auth import views as auth_views
from django.conf.urls.i18n import i18n_patterns
from nodes import views
from clients import views as cl_views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^admin/', admin.site.urls),
    url(r'^dashboard/$', cl_views.dashboard, name='clients_dashboard'),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='clients/login.html'), name='clients_login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(template_name='clients/logged_out.html'), name='clients_logout'),
    url(r'^become_creator/$', cl_views.signup_user, name='clients_signup'),
    url(r'^plans/$', cl_views.plans, name='client_plans'),
    url(r'^tap_payment/(?P<subscription_id>\d+)/$', cl_views.tap_payment, name='tap_payment'),
    url(r'^tap_payment_post/(?P<subscription_id>\d+)/(?P<profile_id>\d+)/$', cl_views.tap_payment_post, name='tap_payment_post'),
    url(r'^student/$', views.student, name='student'),
    url(r'^business/$', views.business, name='business'),
    url(r'^individual/$', views.individual, name='individual'),
    url(r'^library/$', views.library, name='library'),
    url(r'^about/$', views.about, name='about'),
    url(r'^privacy_policy/$', views.privacy_policy, name='privacy_policy'),
    url(r'^terms_and_conditions/$', views.terms_and_conditions, name='terms_and_conditions'),
    url(r'^support/$', views.support, name='support'),
    url(r'^contact_us/$', views.contact_us, name='contact_us'),
    url(r'^nodes/$', views.nodes_list, name='nodes_list'),
    url(r'^nodes/(?P<sort>[-\w]+)$', views.nodes_list, name='nodes_list'),
    url(r'^node/(?P<slug>[-\w]+)/$', views.nodes_detail, name='nodes_detail'),
    url(r'^node_unlock/(?P<node_id>\d+)/$', views.node_unlock, name='node_unlock'),
    url(r'^node_update/add_like/(?P<node_id>\d+)/$', views.node_update_likes, name='node_update_likes'),
    url(r'^play/(?P<node_id>\d+)/$', views.node_play, name='node_play'),
    url(r'^channels/$', views.channels_list, name='channels_list'),
    url(r'^channels/(?P<page_id>\d+)$', views.channels_list, name='channels_list'),
    url(r'^channels/(?P<slug>[-\w]+)/$', views.channel_detail, name='channel_detail'),
    url(r'^channels/(?P<slug_channel>[-\w]+)/(?P<slug_subchannel>[-\w]+)/$', views.subchannel_detail, name='subchannel_detail'),
    url(r'^channels/(?P<slug_channel>[-\w]+)/node/(?P<slug>[-\w]+)/$', views.nodes_detail, name='nodes_detail'),
    url(r'i18n/', include('django.conf.urls.i18n')),
]
