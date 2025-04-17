from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Group(models.Model):
    name_group = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(upload_to='groups/', null=True, blank=True)

    def __str__(self):
        return self.name_group

class Album(models.Model):
    name_album = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    release_date = models.DateField()
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)
    photo = models.ImageField(upload_to='albums/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='albums')

    def __str__(self):
        return f"{self.name_album} - {self.group.name_group}"

class Composition(models.Model):
    name_composition = models.CharField(max_length=255)
    duration = models.IntegerField(help_text="Duration in seconds")
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)
    photo = models.ImageField(upload_to='compositions/', null=True, blank=True)
    reference_on_file = models.FileField(upload_to='music_files/')
    lyrics = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='compositions')
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f"{self.name_composition} - {self.album.group.name_group}"

    class Meta:
        ordering = ['album', 'name_composition']

class Playlist(models.Model):
    name_playlist = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    compositions = models.ManyToManyField(Composition, through='PlaylistComposition')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name_playlist

class PlaylistComposition(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    composition = models.ForeignKey(Composition, on_delete=models.CASCADE)
    position = models.IntegerField()
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position']
        unique_together = ['playlist', 'position']

class ParticipantInfo(models.Model):
    name = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    surname = models.CharField(max_length=100, blank=True)
    date_birth = models.DateField()
    photo = models.ImageField(upload_to='participants/', null=True, blank=True)
    biography = models.TextField(blank=True)
    groups = models.ManyToManyField(Group, related_name='participants')

    def __str__(self):
        return f"{self.name} {self.lastname}"

class ParticipantRole(models.Model):
    name_role = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name_role

class CompositionParticipant(models.Model):
    composition = models.ForeignKey(Composition, on_delete=models.CASCADE)
    participant = models.ForeignKey(ParticipantInfo, on_delete=models.CASCADE)
    role = models.ForeignKey(ParticipantRole, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['composition', 'participant', 'role']

class Evaluation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    composition = models.ForeignKey(Composition, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'composition']

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    composition = models.ForeignKey(Composition, on_delete=models.CASCADE)
    feedback_text = models.TextField()
    is_moderated = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

class UserListeningHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    composition = models.ForeignKey(Composition, on_delete=models.CASCADE)
    listened_at = models.DateTimeField(auto_now_add=True)
    duration_listened = models.IntegerField(help_text="Duration listened in seconds")

class UserFollower(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['follower', 'following']
