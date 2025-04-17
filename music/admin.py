from django.contrib import admin
from .models import (
    Genre, Tag, Composition, Album, Playlist, Group,
    ParticipantInfo, ParticipantRole, CompositionParticipant,
    Evaluation, Feedback, UserListeningHistory, UserFollower,
    PlaylistComposition
)

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Composition)
class CompositionAdmin(admin.ModelAdmin):
    list_display = ('name_composition', 'duration', 'genre', 'album', 'date')
    list_filter = ('genre', 'album', 'date')
    search_fields = ('name_composition',)
    filter_horizontal = ('tags',)

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('name_album', 'group', 'genre', 'release_date', 'created_at')
    list_filter = ('group', 'genre', 'release_date')
    search_fields = ('name_album', 'group__name_group')

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name_playlist', 'user', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('name_playlist', 'user__username')

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name_group', 'created_at')
    search_fields = ('name_group',)

@admin.register(ParticipantInfo)
class ParticipantInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'lastname', 'surname', 'date_birth')
    search_fields = ('name', 'lastname')
    filter_horizontal = ('groups',)

@admin.register(ParticipantRole)
class ParticipantRoleAdmin(admin.ModelAdmin):
    list_display = ('name_role', 'description')
    search_fields = ('name_role',)

@admin.register(CompositionParticipant)
class CompositionParticipantAdmin(admin.ModelAdmin):
    list_display = ('composition', 'participant', 'role')
    list_filter = ('role',)
    search_fields = ('composition__name_composition', 'participant__name')

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('user', 'composition', 'rating', 'date')
    list_filter = ('rating', 'date')
    search_fields = ('user__username', 'composition__name_composition')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'composition', 'is_moderated', 'date')
    list_filter = ('is_moderated', 'date')
    search_fields = ('user__username', 'composition__name_composition')

@admin.register(UserListeningHistory)
class UserListeningHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'composition', 'listened_at', 'duration_listened')
    list_filter = ('listened_at',)
    search_fields = ('user__username', 'composition__name_composition')
