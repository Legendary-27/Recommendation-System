# -*- coding: utf-8 -*-
from django.urls import path
from . import views

app_name = 'cms'

urlpatterns = [
        path('',views.cms_index,name='cms_index'),
        path('register/',views.register,name="register"),
        path('logout/',views.logout,name="logout"),
        path('add_news/',views.news_add,name='news_add'),
        path('new_detail/<new_id>/',views.news_detail,name='news_detail'),
        path('delete_news/',views.news_delate,name='news_delate'),
    ]
