from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Fieldset, HTML
from .models import Game, GameFile, GameImage, Genre


class GameForm(forms.ModelForm):
    """Форма создания/редактирования игры"""
    
    class Meta:
        model = Game
        fields = [
            'title', 'short_description', 'description', 'cover_image', 'banner_image',
            'genres', 'tags',
            'windows_support', 'mac_support', 'linux_support', 'android_support', 'ios_support'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 8}),
            'short_description': forms.Textarea(attrs={'rows': 3}),
            'genres': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Основная информация',
                'title',
                'short_description',
                'description',
            ),
            Fieldset(
                'Медиа',
                Row(
                    Column('cover_image', css_class='form-group col-md-6 mb-0'),
                    Column('banner_image', css_class='form-group col-md-6 mb-0'),
                ),
            ),
            Fieldset(
                'Категоризация',
                'genres',
                'tags',
            ),
            Fieldset(
                'Поддерживаемые платформы',
                Row(
                    Column('windows_support', css_class='form-group col-md-4 mb-0'),
                    Column('mac_support', css_class='form-group col-md-4 mb-0'),
                    Column('linux_support', css_class='form-group col-md-4 mb-0'),
                ),
                Row(
                    Column('android_support', css_class='form-group col-md-6 mb-0'),
                    Column('ios_support', css_class='form-group col-md-6 mb-0'),
                ),
            ),
            Submit('submit', 'Сохранить', css_class='btn btn-primary')
        )
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class GameFileForm(forms.ModelForm):
    """Форма загрузки файлов игры"""
    
    class Meta:
        model = GameFile
        fields = ['name', 'file', 'platform', 'version']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'file',
            Row(
                Column('platform', css_class='form-group col-md-6 mb-0'),
                Column('version', css_class='form-group col-md-6 mb-0'),
            ),
            Submit('submit', 'Загрузить', css_class='btn btn-primary')
        )


class GameImageForm(forms.ModelForm):
    """Форма загрузки скриншотов"""
    
    class Meta:
        model = GameImage
        fields = ['image', 'caption', 'order']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'image',
            'caption',
            'order',
            Submit('submit', 'Загрузить', css_class='btn btn-primary')
        )


class GameSearchForm(forms.Form):
    """Форма поиска игр"""
    
    SORT_CHOICES = [
        ('', 'По умолчанию'),
        ('-created_at', 'Новые'),
        ('-download_count', 'Популярные'),
        ('title', 'По алфавиту'),
    ]
    
    q = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Поиск по названию, описанию или тегам...',
            'class': 'form-control'
        }),
        label=''
    )
    
    genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        label='Жанры'
    )
    
    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        label='Сортировка'
    )
    
    # Платформы
    windows = forms.BooleanField(required=False, label='Windows')
    mac = forms.BooleanField(required=False, label='macOS')
    linux = forms.BooleanField(required=False, label='Linux')
    android = forms.BooleanField(required=False, label='Android')
    ios = forms.BooleanField(required=False, label='iOS')


class GamePublishForm(forms.ModelForm):
    """Форма публикации игры"""
    
    class Meta:
        model = Game
        fields = ['is_published']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<div class="alert alert-info">'
                 '<strong>Внимание!</strong> '
                 'После публикации игра станет доступна всем пользователям.'
                 '</div>'),
            'is_published',
            Submit('submit', 'Опубликовать', css_class='btn btn-success')
        )


# Формсеты для множественного добавления файлов и изображений
GameFileFormSet = inlineformset_factory(
    Game, GameFile,
    fields=['name', 'file', 'platform', 'version'],
    extra=1,
    can_delete=True
)

GameImageFormSet = inlineformset_factory(
    Game, GameImage,
    fields=['image', 'caption', 'order'],
    extra=1,
    can_delete=True
)
