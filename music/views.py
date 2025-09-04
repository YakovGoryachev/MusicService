from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import (
    Track, Album, Playlist, Genre, Rating, Comment, 
    User, Group, Artist, ArtistGroup, TrackGenre, PlaylistTrack
)
from .forms import UserRegistrationForm, UserLoginForm, PlaylistForm, CommentForm, TrackCreateForm
import json


def home(request):
    """Главная страница"""
    latest_tracks = Track.objects.select_related('album', 'album__artist', 'album__group').order_by('-id')[:8]
    popular_albums = Album.objects.select_related('artist', 'group').order_by('-play_count')[:4]
    genres = Genre.objects.all()[:6]
    
    context = {
        'latest_tracks': latest_tracks,
        'popular_albums': popular_albums,
        'genres': genres,
    }
    return render(request, 'music/home.html', context)


def track_list(request):
    """Список всех треков"""
    query = request.GET.get('q', '')
    genre_filter = request.GET.get('genre', '')
    
    tracks = Track.objects.select_related('album', 'album__artist', 'album__group').prefetch_related('genres')
    
    if query:
        tracks = tracks.filter(
            Q(name__icontains=query) |
            Q(album__name__icontains=query) |
            Q(album__artist__name__icontains=query) |
            Q(album__group__name__icontains=query) |
            Q(genres__name__icontains=query)
        ).distinct()
    
    if genre_filter:
        tracks = tracks.filter(genres__name=genre_filter)
    
    tracks = tracks.order_by('-id')
    
    paginator = Paginator(tracks, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    genres = Genre.objects.all()
    
    context = {
        'tracks': page_obj,
        'genres': genres,
        'query': query,
        'genre_filter': genre_filter,
    }
    return render(request, 'music/track_list.html', context)


def track_detail(request, pk):
    """Детальная страница трека"""
    track = get_object_or_404(Track.objects.select_related('album', 'album__artist', 'album__group').prefetch_related('genres'), pk=pk)
    
    # Получаем оценки и комментарии
    ratings = Rating.objects.filter(track=track).select_related('user')
    comments = Comment.objects.filter(track=track).select_related('user').order_by('-created_at')
    
    # Средняя оценка
    avg_rating = ratings.aggregate(avg=Avg('value'))['avg'] or 0
    
    # Пользовательская оценка
    user_rating = None
    if request.user.is_authenticated:
        user_rating = ratings.filter(user=request.user).first()
    
    # Увеличиваем счетчик прослушиваний
    track.play_count += 1
    track.save()
    
    context = {
        'track': track,
        'ratings': ratings,
        'comments': comments,
        'avg_rating': round(avg_rating, 1),
        'user_rating': user_rating,
        'comment_form': CommentForm(),
    }
    return render(request, 'music/track_detail.html', context)


def album_list(request):
    """Список альбомов"""
    albums = Album.objects.select_related('artist', 'group').order_by('-release_date')
    
    paginator = Paginator(albums, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'albums': page_obj,
    }
    return render(request, 'music/album_list.html', context)


def album_detail(request, pk):
    """Детальная страница альбома"""
    album = get_object_or_404(Album.objects.select_related('artist', 'group'), pk=pk)
    tracks = album.track_set.all().order_by('id')
    
    context = {
        'album': album,
        'tracks': tracks,
    }
    return render(request, 'music/album_detail.html', context)


def artist_list(request):
    """Список артистов"""
    artists = Artist.objects.all().order_by('name')
    
    paginator = Paginator(artists, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'artists': page_obj,
    }
    return render(request, 'music/artist_list.html', context)


def artist_detail(request, pk):
    """Детальная страница артиста"""
    artist = get_object_or_404(Artist, pk=pk)
    albums = artist.album_set.all().order_by('-release_date')
    
    context = {
        'artist': artist,
        'albums': albums,
    }
    return render(request, 'music/artist_detail.html', context)


def group_list(request):
    """Список групп"""
    groups = Group.objects.all().order_by('name')
    
    paginator = Paginator(groups, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'groups': page_obj,
    }
    return render(request, 'music/group_list.html', context)


def group_detail(request, pk):
    """Детальная страница группы"""
    group = get_object_or_404(Group, pk=pk)
    albums = group.album_set.all().order_by('-release_date')
    artists = group.artist_set.all()
    
    context = {
        'group': group,
        'albums': albums,
        'artists': artists,
    }
    return render(request, 'music/group_detail.html', context)


def playlist_list(request):
    """Список публичных плейлистов"""
    playlists = Playlist.objects.filter(is_public=True).select_related('user').prefetch_related('tracks')
    
    paginator = Paginator(playlists, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'playlists': page_obj,
    }
    return render(request, 'music/playlist_list.html', context)


def playlist_detail(request, pk):
    """Детальная страница плейлиста"""
    playlist = get_object_or_404(Playlist.objects.select_related('user').prefetch_related('tracks'), pk=pk)
    
    if not playlist.is_public and request.user != playlist.user:
        messages.error(request, 'Этот плейлист приватный')
        return redirect('music:playlist_list')
    
    context = {
        'playlist': playlist,
    }
    return render(request, 'music/playlist_detail.html', context)


@login_required
def my_playlists(request):
    """Мои плейлисты"""
    playlists = Playlist.objects.filter(user=request.user).prefetch_related('tracks')
    
    context = {
        'playlists': playlists,
    }
    return render(request, 'music/my_playlists.html', context)


@login_required
def create_playlist(request):
    """Создание плейлиста"""
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.user = request.user
            playlist.save()
            messages.success(request, 'Плейлист создан успешно!')
            return redirect('music:playlist_detail', pk=playlist.pk)
    else:
        form = PlaylistForm()
    
    context = {
        'form': form,
    }
    return render(request, 'music/create_playlist.html', context)


@login_required
def edit_playlist(request, pk):
    """Редактирование плейлиста"""
    playlist = get_object_or_404(Playlist, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = PlaylistForm(request.POST, instance=playlist)
        if form.is_valid():
            form.save()
            messages.success(request, 'Плейлист обновлен!')
            return redirect('music:playlist_detail', pk=playlist.pk)
    else:
        form = PlaylistForm(instance=playlist)
    
    context = {
        'form': form,
        'playlist': playlist,
    }
    return render(request, 'music/edit_playlist.html', context)


@login_required
def delete_playlist(request, pk):
    """Удаление плейлиста"""
    playlist = get_object_or_404(Playlist, pk=pk, user=request.user)
    
    if request.method == 'POST':
        playlist.delete()
        messages.success(request, 'Плейлист удален!')
        return redirect('music:my_playlists')
    
    context = {
        'playlist': playlist,
    }
    return render(request, 'music/delete_playlist.html', context)


@login_required
@require_POST
def add_to_playlist(request, track_id):
    """Добавление трека в плейлист"""
    track = get_object_or_404(Track, pk=track_id)
    playlist_id = request.POST.get('playlist_id')
    
    if playlist_id:
        playlist = get_object_or_404(Playlist, pk=playlist_id, user=request.user)
        playlist.tracks.add(track)
        messages.success(request, f'Трек "{track.name}" добавлен в плейлист "{playlist.name}"!')
    else:
        messages.error(request, 'Выберите плейлист!')
        
    return redirect('music:track_detail', pk=track_id)


@login_required
@require_POST
def remove_from_playlist(request, playlist_id, track_id):
    """Удаление трека из плейлиста"""
    playlist = get_object_or_404(Playlist, pk=playlist_id, user=request.user)
    track = get_object_or_404(Track, pk=track_id)
    
    playlist.tracks.remove(track)
    messages.success(request, f'Трек "{track.name}" удален из плейлиста!')
    
    return redirect('music:playlist_detail', pk=playlist_id)


@login_required
@require_POST
def rate_track(request, track_id):
    """Оценка трека"""
    track = get_object_or_404(Track, pk=track_id)
    rating_value = request.POST.get('rating')
    
    if rating_value and rating_value.isdigit():
        rating_value = int(rating_value)
        if 1 <= rating_value <= 5:
            rating, created = Rating.objects.get_or_create(
                user=request.user,
                track=track,
                defaults={'value': rating_value}
            )
            if not created:
                rating.value = rating_value
                rating.save()
            
            messages.success(request, 'Оценка сохранена!')
        else:
            messages.error(request, 'Оценка должна быть от 1 до 5!')
    else:
        messages.error(request, 'Выберите оценку!')
    
    return redirect('music:track_detail', pk=track_id)


@login_required
@require_POST
def add_comment(request, track_id):
    """Добавление комментария к треку"""
    track = get_object_or_404(Track, pk=track_id)
    form = CommentForm(request.POST)
    
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.track = track
        comment.save()
        messages.success(request, 'Комментарий добавлен!')
    else:
        messages.error(request, 'Ошибка в форме комментария!')
    
    return redirect('music:track_detail', pk=track_id)


@login_required
def delete_comment(request, comment_id):
    """Удаление комментария"""
    comment = get_object_or_404(Comment, pk=comment_id, user=request.user)
    track_id = comment.track.id
    
    comment.delete()
    messages.success(request, 'Комментарий удален!')
    
    return redirect('music:track_detail', pk=track_id)


def user_register(request):
    """Регистрация пользователя"""
    if request.user.is_authenticated:
        return redirect('music:home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('music:home')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'music/register.html', context)


def user_login(request):
    """Вход пользователя"""
    if request.user.is_authenticated:
        return redirect('music:home')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user_login = form.cleaned_data['login']
            password = form.cleaned_data['password']
            user = authenticate(request, username=user_login, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.login}!')
                return redirect('music:home')
            else:
                messages.error(request, 'Неверный логин или пароль!')
    else:
        form = UserLoginForm()
    
    context = {
        'form': form,
    }
    return render(request, 'music/login.html', context)


def user_logout(request):
    """Выход пользователя"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы!')
    return redirect('music:home')


@login_required
def profile(request):
    """Профиль пользователя"""
    user_playlists = Playlist.objects.filter(user=request.user).prefetch_related('tracks')
    user_ratings = Rating.objects.filter(user=request.user).select_related('track', 'track__album')
    
    context = {
        'user_playlists': user_playlists,
        'user_ratings': user_ratings,
    }
    return render(request, 'music/profile.html', context)


# API представления для AJAX
@csrf_exempt
@require_POST
def api_rate_track(request, track_id):
    """API для оценки трека"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Не авторизован'}, status=401)
    
    try:
        data = json.loads(request.body)
        rating_value = int(data.get('rating', 0))
        
        if not (1 <= rating_value <= 5):
            return JsonResponse({'error': 'Оценка должна быть от 1 до 5'}, status=400)
        
        track = get_object_or_404(Track, pk=track_id)
        rating, created = Rating.objects.get_or_create(
            user=request.user,
            track=track,
            defaults={'value': rating_value}
        )
        
        if not created:
            rating.value = rating_value
            rating.save()
        
        return JsonResponse({'success': True, 'rating': rating_value})
    
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({'error': 'Неверные данные'}, status=400)


@csrf_exempt
@require_POST
def api_add_comment(request, track_id):
    """API для добавления комментария"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Не авторизован'}, status=401)
    
    try:
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        
        if not text:
            return JsonResponse({'error': 'Текст комментария не может быть пустым'}, status=400)
        
        track = get_object_or_404(Track, pk=track_id)
        comment = Comment.objects.create(
                user=request.user,
            track=track,
            text=text
        )
        
        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'text': comment.text,
                'user': comment.user.login,
                'created_at': comment.created_at.isoformat()
            }
        })
    
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({'error': 'Неверные данные'}, status=400)


# Админ панель представления
@login_required
def admin_panel(request):
    """Главная страница админ панели"""
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Доступ запрещен. Требуются права администратора.')
        return redirect('music:home')
    
    # Статистика
    total_tracks = Track.objects.count()
    total_albums = Album.objects.count()
    total_artists = Artist.objects.count()
    total_groups = Group.objects.count()
    
    context = {
        'total_tracks': total_tracks,
        'total_albums': total_albums,
        'total_artists': total_artists,
        'total_groups': total_groups,
    }
    return render(request, 'music/admin/admin_panel.html', context)


@login_required
def admin_tracks(request):
    """Управление треками"""
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Доступ запрещен. Требуются права администратора.')
        return redirect('music:home')
    
    tracks = Track.objects.select_related('album', 'album__artist', 'album__group').prefetch_related('genres').order_by('-id')
    
    context = {
        'tracks': tracks,
    }
    return render(request, 'music/admin/admin_tracks.html', context)


@login_required
def admin_create_track(request):
    """Создание нового трека"""
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Доступ запрещен. Требуются права администратора.')
        return redirect('music:home')
    
    if request.method == 'POST':
        form = TrackCreateForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Получаем данные из формы
                name = form.cleaned_data['name']
                file = form.cleaned_data['file']
                duration = form.cleaned_data.get('duration')
                artist_name = form.cleaned_data.get('artist_name')
                group_name = form.cleaned_data.get('group_name')
                album_name = form.cleaned_data.get('album_name')
                album_release_date = form.cleaned_data.get('album_release_date')
                genre_names = form.cleaned_data.get('genre_names', [])
                
                # Создаем или получаем артиста/группу
                artist = None
                group = None
                
                if group_name:
                    group, created = Group.objects.get_or_create(name=group_name)
                    if created:
                        messages.info(request, f'Создана новая группа: {group_name}')
                
                if artist_name:
                    artist, created = Artist.objects.get_or_create(name=artist_name)
                    if created:
                        messages.info(request, f'Создан новый артист: {artist_name}')
                
                # Создаем или получаем альбом
                album = None
                if album_name:
                    album, created = Album.objects.get_or_create(
                        name=album_name,
                        defaults={
                            'artist': artist,
                            'group': group,
                            'release_date': album_release_date
                        }
                    )
                    if created:
                        messages.info(request, f'Создан новый альбом: {album_name}')
                
                # Создаем трек
                track = Track.objects.create(
                    name=name,
                    file=file,
                    album=album,
                    duration=duration
                )
                
                # Создаем или получаем жанры
                for genre_name in genre_names:
                    if genre_name:
                        genre, created = Genre.objects.get_or_create(name=genre_name)
                        if created:
                            messages.info(request, f'Создан новый жанр: {genre_name}')
                        TrackGenre.objects.create(track=track, genre=genre)
                
                messages.success(request, f'Трек "{name}" успешно создан!')
                return redirect('music:admin_tracks')
                
            except Exception as e:
                messages.error(request, f'Ошибка создания трека: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = TrackCreateForm()
    
    context = {
        'form': form,
    }
    return render(request, 'music/admin/admin_create_track.html', context)


@login_required
def admin_edit_track(request, pk):
    """Редактирование трека"""
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Доступ запрещен. Требуются права администратора.')
        return redirect('music:home')
    
    track = get_object_or_404(Track, pk=pk)
    
    if request.method == 'POST':
        # Обработка редактирования трека
        name = request.POST.get('name')
        album_id = request.POST.get('album')
        duration = request.POST.get('duration')
        file_url = request.POST.get('file_url')
        genre_ids = request.POST.getlist('genres')
        
        if name and album_id and duration and file_url:
            try:
                album = Album.objects.get(pk=album_id)
                track.name = name
                track.album = album
                track.duration = int(duration)
                track.file_url = file_url
                track.save()
                
                # Обновляем жанры
                track.genres.clear()
                for genre_id in genre_ids:
                    if genre_id:
                        genre = Genre.objects.get(pk=genre_id)
                        TrackGenre.objects.create(track=track, genre=genre)
                
                messages.success(request, f'Трек "{name}" успешно обновлен!')
                return redirect('music:admin_tracks')
            except Exception as e:
                messages.error(request, f'Ошибка обновления трека: {str(e)}')
        else:
            messages.error(request, 'Заполните все обязательные поля!')
    
    albums = Album.objects.all()
    genres = Genre.objects.all()
    selected_genres = [genre.id for genre in track.genres.all()]
    
    context = {
        'track': track,
        'albums': albums,
        'genres': genres,
        'selected_genres': selected_genres,
    }
    return render(request, 'music/admin/admin_edit_track.html', context)


@login_required
def admin_delete_track(request, pk):
    """Удаление трека"""
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Доступ запрещен. Требуются права администратора.')
        return redirect('music:home')
    
    track = get_object_or_404(Track, pk=pk)
    
    if request.method == 'POST':
        track_name = track.name
        track.delete()
        messages.success(request, f'Трек "{track_name}" успешно удален!')
        return redirect('music:admin_tracks')
    
    context = {
        'track': track,
    }
    return render(request, 'music/admin/admin_delete_track.html', context)


@login_required
def admin_albums(request):
    """Управление альбомами"""
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Доступ запрещен. Требуются права администратора.')
        return redirect('music:home')
    
    albums = Album.objects.select_related('artist', 'group').order_by('-id')
    
    context = {
        'albums': albums,
    }
    return render(request, 'music/admin/admin_albums.html', context)


@login_required
def admin_edit_album(request, album_id):
    """Редактирование альбома"""
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Доступ запрещен. Требуются права администратора.')
        return redirect('music:home')
    
    try:
        album = Album.objects.get(id=album_id)
    except Album.DoesNotExist:
        messages.error(request, 'Альбом не найден!')
        return redirect('music:admin_albums')
    
    if request.method == 'POST':
        # Обработка редактирования альбома
        name = request.POST.get('name')
        artist_id = request.POST.get('artist')
        group_id = request.POST.get('group')
        release_date = request.POST.get('release_date')
        photo = request.FILES.get('photo')
        
        if name and (artist_id or group_id):
            try:
                artist = None
                group = None
                
                if artist_id:
                    artist = Artist.objects.get(pk=artist_id)
                if group_id:
                    group = Group.objects.get(pk=group_id)
                
                album.name = name
                album.artist = artist
                album.group = group
                album.release_date = release_date if release_date else None
                
                # Обновляем фото только если загружено новое
                if photo:
                    album.photo = photo
                
                album.save()
                
                messages.success(request, f'Альбом "{name}" успешно обновлен!')
                return redirect('music:admin_albums')
            except Exception as e:
                messages.error(request, f'Ошибка обновления альбома: {str(e)}')
        else:
            messages.error(request, 'Заполните все обязательные поля!')
    
    artists = Artist.objects.all()
    groups = Group.objects.all()
    
    context = {
        'album': album,
        'artists': artists,
        'groups': groups,
    }
    return render(request, 'music/admin/admin_edit_album.html', context)


@login_required
def admin_delete_album(request, album_id):
    """Удаление альбома"""
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Доступ запрещен. Требуются права администратора.')
        return redirect('music:home')
    
    try:
        album = Album.objects.get(id=album_id)
        album_name = album.name
        album.delete()
        messages.success(request, f'Альбом "{album_name}" успешно удален!')
    except Album.DoesNotExist:
        messages.error(request, 'Альбом не найден!')
    except Exception as e:
        messages.error(request, f'Ошибка удаления альбома: {str(e)}')
    
    return redirect('music:admin_albums')


@login_required
def admin_create_album(request):
    """Создание нового альбома"""
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Доступ запрещен. Требуются права администратора.')
        return redirect('music:home')
    
    if request.method == 'POST':
        # Обработка создания альбома
        name = request.POST.get('name')
        artist_id = request.POST.get('artist')
        group_id = request.POST.get('group')
        release_date = request.POST.get('release_date')
        photo = request.FILES.get('photo')
        
        if name and (artist_id or group_id):
            try:
                artist = None
                group = None
                
                if artist_id:
                    artist = Artist.objects.get(pk=artist_id)
                if group_id:
                    group = Group.objects.get(pk=group_id)
                
                album = Album.objects.create(
                    name=name,
                    artist=artist,
                    group=group,
                    release_date=release_date if release_date else None,
                    photo=photo if photo else None
                )
                
                messages.success(request, f'Альбом "{name}" успешно создан!')
                return redirect('music:admin_albums')
            except Exception as e:
                messages.error(request, f'Ошибка создания альбома: {str(e)}')
        else:
            messages.error(request, 'Заполните все обязательные поля!')
    
    artists = Artist.objects.all()
    groups = Group.objects.all()
    
    context = {
        'artists': artists,
        'groups': groups,
    }
    return render(request, 'music/admin/admin_create_album.html', context)


@login_required
def admin_artists(request):
    """Управление артистами"""
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Доступ запрещен. Требуются права администратора.')
        return redirect('music:home')
    
    artists = Artist.objects.all().order_by('-id')
    
    context = {
        'artists': artists,
    }
    return render(request, 'music/admin/admin_artists.html', context)


@login_required
def admin_create_artist(request):
    """Создание нового артиста"""
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Доступ запрещен. Требуются права администратора.')
        return redirect('music:home')
    
    if request.method == 'POST':
        # Обработка создания артиста
        name = request.POST.get('name')
        bio = request.POST.get('bio')
        artist_role = request.POST.get('artist_role')
        avatar = request.FILES.get('avatar')
        
        if name:
            try:
                artist = Artist.objects.create(
                    name=name,
                    biography=bio if bio else '',
                    artist_role=artist_role if artist_role else '',
                    avatar=avatar if avatar else None
                )
                
                messages.success(request, f'Артист "{name}" успешно создан!')
                return redirect('music:admin_artists')
            except Exception as e:
                messages.error(request, f'Ошибка создания артиста: {str(e)}')
        else:
            messages.error(request, 'Заполните все обязательные поля!')
    
    context = {}
    return render(request, 'music/admin/admin_create_artist.html', context)


@login_required
def admin_edit_artist(request, artist_id):
    """Редактирование артиста"""
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Доступ запрещен. Требуются права администратора.')
        return redirect('music:home')
    
    try:
        artist = Artist.objects.get(id=artist_id)
    except Artist.DoesNotExist:
        messages.error(request, 'Артист не найден!')
        return redirect('music:admin_artists')
    
    if request.method == 'POST':
        # Обработка редактирования артиста
        name = request.POST.get('name')
        bio = request.POST.get('bio')
        artist_role = request.POST.get('artist_role')
        avatar = request.FILES.get('avatar')
        
        if name:
            try:
                artist.name = name
                artist.biography = bio if bio else ''
                artist.artist_role = artist_role if artist_role else ''
                
                # Обновляем фото только если загружено новое
                if avatar:
                    artist.avatar = avatar
                
                artist.save()
                
                messages.success(request, f'Артист "{name}" успешно обновлен!')
                return redirect('music:admin_artists')
            except Exception as e:
                messages.error(request, f'Ошибка обновления артиста: {str(e)}')
        else:
            messages.error(request, 'Заполните все обязательные поля!')
    
    context = {
        'artist': artist,
    }
    return render(request, 'music/admin/admin_edit_artist.html', context)


@login_required
def admin_delete_artist(request, artist_id):
    """Удаление артиста"""
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Доступ запрещен. Требуются права администратора.')
        return redirect('music:home')
    
    try:
        artist = Artist.objects.get(id=artist_id)
        artist_name = artist.name
        artist.delete()
        messages.success(request, f'Артист "{artist_name}" успешно удален!')
    except Artist.DoesNotExist:
        messages.error(request, 'Артист не найден!')
    except Exception as e:
        messages.error(request, f'Ошибка удаления артиста: {str(e)}')
    
    return redirect('music:admin_artists')
@login_required
def admin_groups(request):
    """Управление группами"""
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Доступ запрещен. Требуются права администратора.')
        return redirect('music:home')
    
    groups = Group.objects.all().order_by('-id')
    
    context = {
        'groups': groups,
    }
    return render(request, 'music/admin/admin_groups.html', context)


@login_required
def admin_edit_group(request, group_id):
    """Редактирование группы"""
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Доступ запрещен. Требуются права администратора.')
        return redirect('music:home')
    
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        messages.error(request, 'Группа не найдена!')
        return redirect('music:admin_groups')
    
    if request.method == 'POST':
        # Обработка редактирования группы
        name = request.POST.get('name')
        description = request.POST.get('description')
        photo = request.FILES.get('photo')
        
        if name:
            try:
                group.name = name
                group.description = description if description else ''
                
                # Обновляем фото только если загружено новое
                if photo:
                    group.photo = photo
                
                group.save()
                
                messages.success(request, f'Группа "{name}" успешно обновлена!')
                return redirect('music:admin_groups')
            except Exception as e:
                messages.error(request, f'Ошибка обновления группы: {str(e)}')
        else:
            messages.error(request, 'Заполните все обязательные поля!')
    
    context = {
        'group': group,
    }
    return render(request, 'music/admin/admin_edit_group.html', context)


@login_required
def admin_delete_group(request, group_id):
    """Удаление группы"""
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Доступ запрещен. Требуются права администратора.')
        return redirect('music:home')
    
    try:
        group = Group.objects.get(id=group_id)
        group_name = group.name
        group.delete()
        messages.success(request, f'Группа "{group_name}" успешно удалена!')
    except Group.DoesNotExist:
        messages.error(request, 'Группа не найдена!')
    except Exception as e:
        messages.error(request, f'Ошибка удаления группы: {str(e)}')
    
    return redirect('music:admin_groups')


@login_required
def admin_create_group(request):
    """Создание новой группы"""
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Доступ запрещен. Требуются права администратора.')
        return redirect('music:home')
    
    if request.method == 'POST':
        # Обработка создания группы
        name = request.POST.get('name')
        description = request.POST.get('description')
        photo = request.FILES.get('photo')
        
        if name:
            try:
                group = Group.objects.create(
                    name=name,
                    description=description if description else '',
                    photo=photo if photo else None
                )
                
                messages.success(request, f'Группа "{name}" успешно создана!')
                return redirect('music:admin_groups')
            except Exception as e:
                messages.error(request, f'Ошибка создания группы: {str(e)}')
        else:
            messages.error(request, 'Заполните все обязательные поля!')
    
    context = {}
    return render(request, 'music/admin/admin_create_group.html', context)


@login_required
def admin_genres(request):
    """Управление жанрами"""
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Доступ запрещен. Требуются права администратора.')
        return redirect('music:home')
    
    genres = Genre.objects.all().order_by('name')
    
    context = {
        'genres': genres,
    }
    return render(request, 'music/admin/admin_genres.html', context)
