from django.contrib import admin
from django.urls import path, include

from . import views


urlpatterns = [
    path('', views.IndexView.as_view(), name='index-page'),
    path('add', views.AddPhotoView.as_view(), name='add-photo'),
    path('set', views.SetWalletView.as_view(), name='set-wallet'),
]
