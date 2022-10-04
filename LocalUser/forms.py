#Developer : SURENDRA 
#date : 2-Oct-2022
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import LocalUser
from django import forms
from django.contrib.auth import get_user_model


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm):
        model = LocalUser
        fields = '__all__'

