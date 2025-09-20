from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import authenticate
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import User, DeveloperProfile


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    is_developer = forms.BooleanField(
        required=False, 
        label='Я разработчик игр',
        help_text='Отметьте, если вы планируете публиковать игры'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'is_developer')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'email',
            Row(
                Column('password1', css_class='form-group col-md-6 mb-0'),
                Column('password2', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'is_developer',
            Submit('submit', 'Зарегистрироваться', css_class='btn btn-primary')
        )
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_developer = self.cleaned_data['is_developer']
        if commit:
            user.save()
            # Создаем профиль разработчика, если отмечено
            if user.is_developer:
                DeveloperProfile.objects.create(
                    user=user,
                    display_name=user.username,
                    bio=''
                )
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'avatar', 'bio', 
            'date_of_birth', 'location', 'website', 'twitter', 'github',
            'email_notifications', 'public_profile'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
            ),
            'email',
            'avatar',
            'bio',
            Row(
                Column('date_of_birth', css_class='form-group col-md-6 mb-0'),
                Column('location', css_class='form-group col-md-6 mb-0'),
            ),
            'website',
            Row(
                Column('twitter', css_class='form-group col-md-6 mb-0'),
                Column('github', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('email_notifications', css_class='form-group col-md-6 mb-0'),
                Column('public_profile', css_class='form-group col-md-6 mb-0'),
            ),
            Submit('submit', 'Сохранить', css_class='btn btn-primary')
        )


class DeveloperProfileForm(forms.ModelForm):
    class Meta:
        model = DeveloperProfile
        fields = ['display_name', 'company', 'website', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 6}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'display_name',
            'company',
            'website',
            'bio',
            Submit('submit', 'Сохранить', css_class='btn btn-primary')
        )


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label='Имя пользователя')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    remember_me = forms.BooleanField(required=False, label='Запомнить меня')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'password',
            'remember_me',
            Submit('submit', 'Войти', css_class='btn btn-primary w-100')
        )
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError('Неверное имя пользователя или пароль')
            elif not self.user_cache.is_active:
                raise forms.ValidationError('Аккаунт заблокирован')
        
        return self.cleaned_data
    
    def get_user(self):
        return getattr(self, 'user_cache', None)
