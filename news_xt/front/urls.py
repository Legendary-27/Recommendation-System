# -*- coding: utf-8 -*-
from django.urls import path
from . import views

app_name = 'front'

urlpatterns = [
        path('',views.index,name='index'),
        path('redu/',views.redu,name='redu'),
        path('technology/',views.technology,name='keji'),
        path('entertainment/',views.entertainment,name='yule'),
        path('financial/',views.financial,name='caijing'),
        path('military/',views.military,name='junshi'),
        path('international',views.international,name='guoji'),
        path('society/',views.society,name='shehui'),
        path('add/',views.add,name='add'),
        path('cut/',views.cut,name='cut'),
        path('date/',views.date,name='date'),
        path('user_center/',views.usercenter,name='usercenter'),
        path('view/<news_id>',views.view,name="view"),
    ]
