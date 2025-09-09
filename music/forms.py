from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Playlist, Comment, Track, Album, Artist, Group, Genre


class UserRegistrationForm(UserCreationForm):
    """Форма регистрации пользователя"""
    email = forms.EmailField(required=True, help_text='Обязательное поле')
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text='Необязательное поле'
    )
    
    class Meta:
        model = User
        fields = ('login', 'email', 'password1', 'password2', 'date_of_birth')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].help_text = 'Уникальное имя пользователя'
        self.fields['password1'].help_text = 'Минимум 8 символов'
        self.fields['password2'].help_text = 'Повторите пароль для подтверждения'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email
    
    def clean_login(self):
        login = self.cleaned_data.get('login')
        if User.objects.filter(login=login).exists():
            raise forms.ValidationError('Пользователь с таким логином уже существует')
        return login


class UserLoginForm(forms.Form):
    """Форма входа пользователя"""
    login = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Введите логин',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Введите пароль'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        login = cleaned_data.get('login')
        password = cleaned_data.get('password')
        
        if not login and not password:
            raise forms.ValidationError('Введите логин и пароль')
        elif not login:
            raise forms.ValidationError('Введите логин')
        elif not password:
            raise forms.ValidationError('Введите пароль')
            
        return cleaned_data


class PlaylistForm(forms.ModelForm):
    """Форма создания/редактирования плейлиста"""
    class Meta:
        model = Playlist
        fields = ['name', 'description', 'is_public', 'photo', 'genres']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название плейлиста'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Описание плейлиста (необязательно)'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'genres': forms.SelectMultiple(attrs={
                'class': 'form-select'
            })
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name.strip():
            raise forms.ValidationError('Название плейлиста не может быть пустым')
        return name.strip()


class CommentForm(forms.ModelForm):
    """Форма добавления комментария"""
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Напишите ваш комментарий...'
            })
        }


class SearchForm(forms.Form):
    """Форма поиска"""
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск по названию, артисту, альбому...'
        })
    )


class TrackCreateForm(forms.ModelForm):
    """Форма создания трека"""
    # Поля для артиста/группы
    artist_name = forms.CharField(
        max_length=200,
        required=False,
        label='Имя артиста',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя артиста (если нет группы)'
        })
    )
    
    group_name = forms.CharField(
        max_length=200,
        required=False,
        label='Название группы',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Название группы (если есть)'
        })
    )
    
    # Поля для альбома
    album_name = forms.CharField(
        max_length=200,
        required=False,
        label='Название альбома',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Название альбома (необязательно)'
        })
    )
    
    album_release_date = forms.DateField(
        required=False,
        label='Дата выпуска альбома',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    # Поля для жанров
    genre_names = forms.CharField(
        max_length=500,
        required=False,
        label='Жанры',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Жанры через запятую (например: рок, поп, электроника)'
        }),
        help_text='Введите жанры через запятую'
    )
    
    class Meta:
        model = Track
        fields = ['name', 'file', 'photo', 'duration']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название трека'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'audio/*'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Длительность в секундах (необязательно)',
                'min': '1'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        artist_name = cleaned_data.get('artist_name')
        group_name = cleaned_data.get('group_name')
        
        # Проверяем, что указан либо артист, либо группа
        if not artist_name and not group_name:
            raise forms.ValidationError('Укажите либо имя артиста, либо название группы')
        
        return cleaned_data
    
    def clean_genre_names(self):
        genre_names = self.cleaned_data.get('genre_names')
        if genre_names:
            # Разбиваем по запятой и очищаем от пробелов
            genres = [name.strip() for name in genre_names.split(',') if name.strip()]
            if not genres:
                raise forms.ValidationError('Введите корректные названия жанров')
            return genres
        return []
