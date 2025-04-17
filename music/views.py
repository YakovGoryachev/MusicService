from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Composition, Album, Playlist, Genre, Evaluation, Feedback

def home(request):
    latest_compositions = Composition.objects.order_by('-date')[:6]
    popular_albums = Album.objects.order_by('-created_at')[:3]
    genres = Genre.objects.all()
    
    context = {
        'latest_compositions': latest_compositions,
        'popular_albums': popular_albums,
        'genres': genres,
    }
    return render(request, 'music/home.html', context)

def composition_list(request):
    query = request.GET.get('q')
    compositions = Composition.objects.all().order_by('-date')
    
    if query:
        compositions = compositions.filter(
            Q(name_composition__icontains=query) |
            Q(album__name_album__icontains=query) |
            Q(genre__name__icontains=query)
        )
    
    paginator = Paginator(compositions, 12)  # 12 композиций на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'music/composition_list.html', {'compositions': page_obj})

def composition_detail(request, pk):
    composition = get_object_or_404(Composition, pk=pk)
    user_rating = None
    if request.user.is_authenticated:
        user_rating = composition.evaluation_set.filter(user=request.user).first()
    
    context = {
        'composition': composition,
        'user_rating': user_rating,
    }
    return render(request, 'music/composition_detail.html', context)

@login_required
def add_to_playlist(request, composition_id):
    if request.method == 'POST':
        composition = get_object_or_404(Composition, id=composition_id)
        playlist_id = request.POST.get('playlist_id')
        
        if playlist_id:
            playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
            position = playlist.playlistcomposition_set.count() + 1
            playlist.playlistcomposition_set.create(
                composition=composition,
                position=position
            )
            messages.success(request, 'Композиция добавлена в плейлист!')
        else:
            messages.error(request, 'Выберите плейлист!')
            
    return redirect('music:composition_detail', pk=composition_id)

@login_required
def create_playlist(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        is_public = request.POST.get('is_public') == 'on'
        
        playlist = Playlist.objects.create(
            name_playlist=name,
            description=description,
            is_public=is_public,
            user=request.user
        )
        messages.success(request, 'Плейлист создан!')
        return redirect('music:playlist_detail', pk=playlist.id)
        
    return render(request, 'music/create_playlist.html')

@login_required
def rate_composition(request, composition_id):
    if request.method == 'POST':
        composition = get_object_or_404(Composition, id=composition_id)
        rating = request.POST.get('rating')
        
        if rating and rating.isdigit() and 1 <= int(rating) <= 5:
            Evaluation.objects.update_or_create(
                user=request.user,
                composition=composition,
                defaults={'rating': int(rating)}
            )
            messages.success(request, 'Оценка сохранена!')
        else:
            messages.error(request, 'Некорректная оценка!')
            
    return redirect('music:composition_detail', pk=composition_id)

@login_required
def add_feedback(request, composition_id):
    if request.method == 'POST':
        composition = get_object_or_404(Composition, id=composition_id)
        feedback_text = request.POST.get('feedback_text')
        
        if feedback_text:
            Feedback.objects.create(
                user=request.user,
                composition=composition,
                feedback_text=feedback_text
            )
            messages.success(request, 'Отзыв добавлен!')
        else:
            messages.error(request, 'Введите текст отзыва!')
            
    return redirect('music:composition_detail', pk=composition_id)
