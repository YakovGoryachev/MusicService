from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Group, Artist, ArtistGroup, Album, Genre, Track, 
    TrackGenre, Playlist, PlaylistTrack, TrackRating, AlbumRating, Comment
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Админ-панель для пользователей"""
    list_display = ('login', 'email', 'role', 'registration_date', 'is_active')
    list_filter = ('role', 'is_active', 'registration_date')
    search_fields = ('login', 'email')
    ordering = ('-registration_date',)
    
    fieldsets = (
        (None, {'fields': ('login', 'password')}),
        ('Персональная информация', {'fields': ('email', 'date_of_birth', 'avatar_url')}),
        ('Разрешения', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'registration_date')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('login', 'email', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Админ-панель для групп"""
    list_display = ('name', 'id')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    """Админ-панель для артистов"""
    list_display = ('name', 'id', 'avatar')
    search_fields = ('name',)
    list_filter = ('biography',)
    ordering = ('name',)


@admin.register(ArtistGroup)
class ArtistGroupAdmin(admin.ModelAdmin):
    """Админ-панель для связи артистов и групп"""
    list_display = ('artist', 'group', 'artist_role')
    list_filter = ('artist_role', 'group')
    search_fields = ('artist__name', 'group__name')
    ordering = ('group__name', 'artist__name')


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    """Админ-панель для альбомов"""
    list_display = ('name', 'group', 'artist', 'release_date', 'play_count')
    list_filter = ('release_date', 'group', 'artist')
    search_fields = ('name', 'group__name', 'artist__name')
    ordering = ('-release_date', 'name')
    date_hierarchy = 'release_date'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Админ-панель для жанров"""
    list_display = ('name', 'id')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    """Админ-панель для треков"""
    list_display = ('name', 'album', 'duration', 'play_count', 'get_genres')
    list_filter = ('album__group', 'album__artist', 'duration')
    search_fields = ('name', 'album__name', 'album__group__name')
    ordering = ('album__name', 'name')
    
    def get_genres(self, obj):
        return ", ".join([genre.name for genre in obj.genres.all()])
    get_genres.short_description = 'Жанры'


@admin.register(TrackGenre)
class TrackGenreAdmin(admin.ModelAdmin):
    """Админ-панель для связи треков и жанров"""
    list_display = ('track', 'genre')
    list_filter = ('genre',)
    search_fields = ('track__name', 'genre__name')
    ordering = ('track__name', 'genre__name')


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    """Админ-панель для плейлистов"""
    list_display = ('name', 'user', 'is_public', 'creation_date', 'get_track_count')
    list_filter = ('is_public', 'creation_date', 'user')
    search_fields = ('name', 'user__login', 'description')
    ordering = ('-creation_date', 'name')
    
    def get_track_count(self, obj):
        return obj.tracks.count()
    get_track_count.short_description = 'Количество треков'


@admin.register(PlaylistTrack)
class PlaylistTrackAdmin(admin.ModelAdmin):
    """Админ-панель для связи плейлистов и треков"""
    list_display = ('playlist', 'track', 'added_date')
    list_filter = ('added_date', 'playlist__user')
    search_fields = ('playlist__name', 'track__name')
    ordering = ('-added_date', 'playlist__name')


@admin.register(TrackRating)
class TrackRatingAdmin(admin.ModelAdmin):
    """Админ-панель для оценок треков"""
    list_display = ('user', 'track', 'value', 'rating_date')
    list_filter = ('value', 'rating_date', 'track__album__group')
    search_fields = ('user__login', 'track__name')
    ordering = ('-rating_date', 'track__name')


@admin.register(AlbumRating)
class AlbumRatingAdmin(admin.ModelAdmin):
    """Админ-панель для оценок альбомов"""
    list_display = ('user', 'album', 'value', 'rating_date')
    list_filter = ('value', 'rating_date', 'album__group')
    search_fields = ('user__login', 'album__name')
    ordering = ('-rating_date', 'album__name')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Админ-панель для комментариев"""
    list_display = ('user', 'track', 'text', 'created_at')
    list_filter = ('created_at', 'track__album__group')
    search_fields = ('user__login', 'track__name', 'text')
    ordering = ('-created_at',)
    list_per_page = 50
