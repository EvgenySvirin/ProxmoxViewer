from django.urls import path

from . import views

app_name = 'connection'
urlpatterns = [
    path('', views.index, name='index'),
    
    path('<int:connection_id>/', views.detail, name='detail'),

    path('<int:connection_id>/results/', views.results, name='results'),

]
