from django.urls import path
from . import views

app_name = 'music'

urlpatterns = [
    path('', views.home, name='home'),
    path('compositions/', views.composition_list, name='composition_list'),
    path('composition/<int:pk>/', views.composition_detail, name='composition_detail'),
    path('composition/<int:composition_id>/add-to-playlist/', views.add_to_playlist, name='add_to_playlist'),
    path('composition/<int:composition_id>/rate/', views.rate_composition, name='rate_composition'),
    path('composition/<int:composition_id>/feedback/', views.add_feedback, name='add_feedback'),
    path('playlist/create/', views.create_playlist, name='create_playlist'),
] 