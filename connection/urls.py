from django.urls import path

from . import views

app_name = 'connection'
urlpatterns = [
    path('auth/', views.auth, name='auth'),
    
    path('auth/<str:username>/', views.user, name='user'),
    
    path('auth/<str:username>/<int:connection_id>/', views.detail, name='detail'),
    
    path('auth/<str:username>/<int:connection_id>/results/', views.results, name='results'),
]



""" 
    path('<int:connection_id>/', views.detail, name='detail'),


    
"""
