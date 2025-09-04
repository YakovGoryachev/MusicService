from django.urls import path
from . import views

app_name = 'music'

urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),
    
    # Аутентификация
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Треки
    path('tracks/', views.track_list, name='track_list'),
    path('track/<uuid:pk>/', views.track_detail, name='track_detail'),
    path('track/<uuid:track_id>/rate/', views.rate_track, name='rate_track'),
    path('track/<uuid:track_id>/comment/', views.add_comment, name='add_comment'),
    path('track/<uuid:track_id>/add-to-playlist/', views.add_to_playlist, name='add_to_playlist'),
    
    # Альбомы
    path('albums/', views.album_list, name='album_list'),
    path('album/<uuid:pk>/', views.album_detail, name='album_detail'),
    
    # Артисты
    path('artists/', views.artist_list, name='artist_list'),
    path('artist/<uuid:pk>/', views.artist_detail, name='artist_detail'),
    
    # Группы
    path('groups/', views.group_list, name='group_list'),
    path('group/<uuid:pk>/', views.group_detail, name='group_detail'),
    
    # Плейлисты
    path('playlists/', views.playlist_list, name='playlist_list'),
    path('playlist/<uuid:pk>/', views.playlist_detail, name='playlist_detail'),
    path('my-playlists/', views.my_playlists, name='my_playlists'),
    path('playlist/create/', views.create_playlist, name='create_playlist'),
    path('playlist/<uuid:pk>/edit/', views.edit_playlist, name='edit_playlist'),
    path('playlist/<uuid:pk>/delete/', views.delete_playlist, name='delete_playlist'),
    path('playlist/<uuid:playlist_id>/remove-track/<uuid:track_id>/', views.remove_from_playlist, name='remove_from_playlist'),
    
    # Комментарии
    path('comment/<uuid:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    
    # API endpoints
    path('api/track/<uuid:track_id>/rate/', views.api_rate_track, name='api_rate_track'),
    path('api/track/<uuid:track_id>/comment/', views.api_add_comment, name='api_add_comment'),
    
    # Админ панель
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/create-track/', views.admin_create_track, name='admin_create_track'),
    path('admin-panel/tracks/', views.admin_tracks, name='admin_tracks'),
    path('admin-panel/track/<uuid:pk>/edit/', views.admin_edit_track, name='admin_edit_track'),
    path('admin-panel/track/<uuid:pk>/delete/', views.admin_delete_track, name='admin_delete_track'),
    path('admin-panel/albums/', views.admin_albums, name='admin_albums'),
    path('admin-panel/create-album/', views.admin_create_album, name='admin_create_album'),
    path('admin-panel/edit-album/<uuid:album_id>/', views.admin_edit_album, name='admin_edit_album'),
    path('admin-panel/delete-album/<uuid:album_id>/', views.admin_delete_album, name='admin_delete_album'),
    path('admin-panel/artists/', views.admin_artists, name='admin_artists'),
    path('admin-panel/create-artist/', views.admin_create_artist, name='admin_create_artist'),
    path('admin-panel/edit-artist/<uuid:artist_id>/', views.admin_edit_artist, name='admin_edit_artist'),
    path('admin-panel/delete-artist/<uuid:artist_id>/', views.admin_delete_artist, name='admin_delete_artist'),
    path('admin-panel/groups/', views.admin_groups, name='admin_groups'),
    path('admin-panel/create-group/', views.admin_create_group, name='admin_create_group'),
    path('admin-panel/edit-group/<uuid:group_id>/', views.admin_edit_group, name='admin_edit_group'),
    path('admin-panel/delete-group/<uuid:group_id>/', views.admin_delete_group, name='admin_delete_group'),
    path('admin-panel/genres/', views.admin_genres, name='admin_genres'),
] 