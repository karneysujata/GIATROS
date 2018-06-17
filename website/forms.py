from django import forms
import datetime
from django.forms.extras.widgets import SelectDateWidget
from .models import User, Profile
import random




class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class appointmentForm(forms.Form):
    slots = [
    ('9:30', '9:30'),
    ('10:30', '10:30'),
    ('11:30', '11:30'),
    ('12:30', '12:30'),
    ('1:30', '1:30'),
    ('2:30', '2:30'),
    ('3:30', '3:30'),
    ('4:30', '4:30'),
    ('5:30', '5:30'),
    ('6:30', '6:30'),
    ]
    scheduled_date = forms.DateField(widget=SelectDateWidget)
    scheduled_time = forms.ChoiceField(choices=slots)


class SearchForm(forms.Form):
    search = forms.CharField(label='',widget=forms.TextInput(attrs={'rows': 1, 'cols': 30, 'placeholder':'Address'}))
    attribute = forms.CharField(label='',widget=forms.TextInput(attrs={'rows': 1, 'cols': 15, 'placeholder':'Filter'}))

class UserRegistrationForm(forms.ModelForm):

    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)


    class Meta:
        model = User
        #From User fields
        fields = ('username', 'first_name', 'email')
        help_texts = {
            'username': None,
            'email': None,
        }

    def clean_password2(self):
        '''Check if both password matches'''
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileEditForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ('gender', 'bdate','photo')
