"""Almari URL Configuration

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
from django.contrib.auth import views as auth_view
from django.urls import path
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.contrib import admin
from search import views
from django.conf.urls import handler404
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name="searchpage" ),
    url(r'^search$', views.search, name="results" ),
    url(r'^error404$', views.error404, name="error404" ),
    url(r'^directaccess$', views.directaccess, name="error" ),
    url(r'^register/$', views.UserFormView.as_view(), name="register" ),
    url(r'^login/$', views.custom_login.as_view(), name="login"),
    url(r'^logout/$', auth_view.LogoutView.as_view(template_name="logout.html"), {'next_page': '/'},  name="logout"),
    url(r'^fav?$', views.get_fav, name="favs"),
    url(r'^add/(?P<Json>(.*)+)$', views.add_to_fav, name="add"),
    url(r'^remove/(?P<Json>(.*)+)$', views.remove, name="remove"),
    url(r'^user/$', views.user, name="user"),
    url(r'^reset/$', views.reset_pass, name="change_password"),
    url(r'^setprofile/$', views.setprofile, name="change_profile")
]

# handler404 = 'search.views.error404'

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)    
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
