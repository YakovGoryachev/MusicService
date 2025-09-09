from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import os


class CustomUserManager(BaseUserManager):
    def create_user(self, login, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(login=login, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(login, email, password, **extra_fields)


class User(AbstractUser):
    """Модель пользователя"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    login = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    date_of_birth = models.DateField(null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    avatar_url = models.URLField(max_length=500, null=True, blank=True)
    role = models.CharField(max_length=20, choices=[
        ('user', 'User'),
        ('admin', 'Admin'),
        ('moderator', 'Moderator')
    ], default='user')
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['email']
    
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.login
        if not self.first_name:
            self.first_name = ''
        if not self.last_name:
            self.last_name = ''
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'пользователи'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return self.login
    
    class Meta:
        db_table = 'пользователи'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return self.login


class Group(models.Model):
    """Модель музыкальной группы"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Название группы')
    description = models.TextField(blank=True, verbose_name='Описание группы')
    photo = models.ImageField(upload_to='groups/', null=True, blank=True, verbose_name='Фото группы')
    
    class Meta:
        db_table = 'группа'
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
    
    def __str__(self):
        return self.name


class Artist(models.Model):
    """Модель артиста"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Имя артиста')
    avatar = models.ImageField(upload_to='artists/', null=True, blank=True, verbose_name='Аватар')
    biography = models.TextField(blank=True, verbose_name='Биография')
    artist_role = models.CharField(max_length=100, blank=True, verbose_name='Роль артиста')
    
    class Meta:
        db_table = 'артисты'
        verbose_name = 'Артист'
        verbose_name_plural = 'Артисты'
    
    def __str__(self):
        return self.name


class ArtistGroup(models.Model):
    """Связующая таблица между артистами и группами"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name='Группа')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, verbose_name='Артист')
    artist_role = models.CharField(max_length=100, verbose_name='Роль артиста в группе')
    
    class Meta:
        db_table = 'артист_группа'
        verbose_name = 'Артист в группе'
        verbose_name_plural = 'Артисты в группах'
        unique_together = ['group', 'artist']
    
    def __str__(self):
        return f"{self.artist.name} - {self.group.name} ({self.artist_role})"


class Album(models.Model):
    """Модель альбома"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Название альбома')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Группа')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Артист')
    release_date = models.DateField(null=True, blank=True, verbose_name='Дата выпуска')
    photo = models.ImageField(upload_to='albums/', null=True, blank=True, verbose_name='Обложка альбома')
    play_count = models.PositiveIntegerField(default=0, verbose_name='Количество прослушиваний')
    
    class Meta:
        db_table = 'альбомы'
        verbose_name = 'Альбом'
        verbose_name_plural = 'Альбомы'
    
    def __str__(self):
        return self.name
    
    @property
    def average_rating(self):
        """Возвращает среднюю оценку альбома"""
        from django.db.models import Avg
        avg = self.ratings.aggregate(avg=Avg('value'))['avg']
        return round(avg, 1) if avg else 0.0
    
    def get_user_rating(self, user):
        """Возвращает оценку пользователя для альбома"""
        if not user.is_authenticated:
            return None
        try:
            return self.ratings.get(user=user).value
        except AlbumRating.DoesNotExist:
            return None
    
    @property
    def tracks_count(self):
        """Возвращает количество треков в альбоме"""
        return self.track_set.count()
    
    @property
    def total_play_count(self):
        """Возвращает общее количество прослушиваний всех треков альбома"""
        from django.db.models import Sum
        total = self.track_set.aggregate(total=Sum('play_count'))['total']
        return total or 0


class Genre(models.Model):
    """Модель жанра"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name='Название жанра')
    
    class Meta:
        db_table = 'жанры'
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
    
    def __str__(self):
        return self.name


class Track(models.Model):
    """Модель трека"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Название трека')
    album = models.ForeignKey(Album, on_delete=models.CASCADE, verbose_name='Альбом', null=True, blank=True)
    duration = models.PositiveIntegerField(verbose_name='Продолжительность (в секундах)', null=True, blank=True)
    file = models.FileField(upload_to='tracks/', verbose_name='Файл трека', null=True, blank=True)
    photo = models.ImageField(upload_to='track_photos/', verbose_name='Фото трека', null=True, blank=True)
    play_count = models.PositiveIntegerField(default=0, verbose_name='Количество прослушиваний')
    genres = models.ManyToManyField(Genre, through='TrackGenre', verbose_name='Жанры')
    
    class Meta:
        db_table = 'трек'
        verbose_name = 'Трек'
        verbose_name_plural = 'Треки'
    
    def __str__(self):
        return self.name
    
    def get_file_url(self):
        """Возвращает URL файла для воспроизведения"""
        if self.file:
            return self.file.url
        return None
    
    @property
    def average_rating(self):
        """Возвращает среднюю оценку трека"""
        from django.db.models import Avg
        avg = self.ratings.aggregate(avg=Avg('value'))['avg']
        return round(avg, 1) if avg else 0.0
    
    def get_user_rating(self, user):
        """Возвращает оценку пользователя для трека"""
        if not user.is_authenticated:
            return None
        try:
            return self.ratings.get(user=user).value
        except TrackRating.DoesNotExist:
            return None
    
    def calculate_duration(self):
        """Рассчитывает длительность трека из файла"""
        if not self.file:
            return None
        
        try:
            # Попробуем использовать mutagen для MP3 файлов
            from mutagen import File as MutagenFile
            audio_file = MutagenFile(self.file.path)
            if audio_file is not None and hasattr(audio_file, 'info'):
                duration = int(audio_file.info.length)
                return duration
        except ImportError:
            # Если mutagen не установлен, попробуем использовать wave для WAV файлов
            try:
                import wave
                if self.file.path.lower().endswith('.wav'):
                    with wave.open(self.file.path, 'rb') as wav_file:
                        frames = wav_file.getnframes()
                        rate = wav_file.getframerate()
                        duration = int(frames / rate)
                        return duration
            except:
                pass
        except Exception:
            pass
        
        return None
    
    def save(self, *args, **kwargs):
        # Если длительность не задана, попробуем рассчитать её
        if not self.duration and self.file:
            calculated_duration = self.calculate_duration()
            if calculated_duration:
                self.duration = calculated_duration
        
        super().save(*args, **kwargs)


class TrackGenre(models.Model):
    """Связующая таблица между треками и жанрами"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    track = models.ForeignKey(Track, on_delete=models.CASCADE, verbose_name='Трек')
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, verbose_name='Жанр')
    
    class Meta:
        db_table = 'треки_жанры'
        verbose_name = 'Жанр трека'
        verbose_name_plural = 'Жанры треков'
        unique_together = ['track', 'genre']
    
    def __str__(self):
        return f"{self.track.name} - {self.genre.name}"


class Playlist(models.Model):
    """Модель плейлиста"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='playlists')
    name = models.CharField(max_length=200, verbose_name='Название плейлиста')
    description = models.TextField(blank=True, verbose_name='Описание')
    is_public = models.BooleanField(default=True, verbose_name='Публичный')
    photo = models.ImageField(upload_to='playlists/', null=True, blank=True, verbose_name='Фото плейлиста')
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    tracks = models.ManyToManyField(Track, through='PlaylistTrack', verbose_name='Треки')
    genres = models.ManyToManyField(Genre, blank=True, verbose_name='Жанры')
    
    class Meta:
        db_table = 'плейлисты'
        verbose_name = 'Плейлист'
        verbose_name_plural = 'Плейлисты'
    
    def __str__(self):
        return f"{self.name} ({self.user.login})"
    
    @property
    def owner(self):
        """Возвращает владельца плейлиста"""
        return self.user


class PlaylistTrack(models.Model):
    """Связующая таблица между плейлистами и треками"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, verbose_name='Плейлист', related_name='playlist_tracks')
    track = models.ForeignKey(Track, on_delete=models.CASCADE, verbose_name='Трек')
    added_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    
    class Meta:
        db_table = 'плейлисты_треки'
        verbose_name = 'Трек в плейлисте'
        verbose_name_plural = 'Треки в плейлистах'
        unique_together = ['playlist', 'track']
    
    def __str__(self):
        return f"{self.track.name} в {self.playlist.name}"


class TrackRating(models.Model):
    """Модель оценки трека"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    value = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Оценка'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    track = models.ForeignKey(Track, on_delete=models.CASCADE, verbose_name='Трек', related_name='ratings')
    rating_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата оценки')
    
    class Meta:
        db_table = 'оценка_трека'
        verbose_name = 'Оценка трека'
        verbose_name_plural = 'Оценки треков'
        unique_together = ['user', 'track']
    
    def __str__(self):
        return f"{self.user.login} оценил {self.track.name} на {self.value}"


class AlbumRating(models.Model):
    """Модель оценки альбома"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    value = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Оценка'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    album = models.ForeignKey(Album, on_delete=models.CASCADE, verbose_name='Альбом', related_name='ratings')
    rating_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата оценки')
    
    class Meta:
        db_table = 'оценка_альбома'
        verbose_name = 'Оценка альбома'
        verbose_name_plural = 'Оценки альбомов'
        unique_together = ['user', 'album']
    
    def __str__(self):
        return f"{self.user.login} оценил {self.album.name} на {self.value}"


class Comment(models.Model):
    """Модель комментария к треку"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    track = models.ForeignKey(Track, on_delete=models.CASCADE, verbose_name='Трек')
    text = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        db_table = 'комментарий'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Комментарий {self.user.login} к {self.track.name}"
