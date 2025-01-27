from django import forms
from django.contrib.auth import authenticate


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        # Autenticar usuario
        Usuario = authenticate(username=username, password=password)
        if Usuario is None:
            # Si no hay coincidencia en la autenticación, lanzar error
            raise forms.ValidationError('Usuario o contraseña incorrectos')

        # Retornar al usuario si es válido
        cleaned_data['Usuario'] = Usuario
        return cleaned_data