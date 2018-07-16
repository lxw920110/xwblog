"""xwblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path,re_path
from CNBLOG import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/',views.login,name='login'),
    path('index/',views.index),
    path('', views.index),
    path('logout/',views.logout),
    path('digg/', views.digg),
    path('comment/',views.comment),

    path('index/backend/',views.backend, name='backend'),
    path('add_article/',views.add_article,name='add_article'),
    re_path('edit_article/?P<id>(\d+)',views.edit_article, name="edit_article"),
    re_path('del_article/',views.delete_article,name="del_article"),
    path('upload/',views.upload),

    re_path('(?P<username>\w+)/articles/(?P<article_id>\d+)$',views.article_detail),
    re_path('(?P<username>\w+)/(?P<condition>category|tag|archive)/(?P<params>.*)',views.homesite),
    re_path('(?P<username>\w+)/$', views.homesite),

]



