from django import forms
from django.contrib.auth.models import User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Hasło', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Powtórz hasło', widget=forms.PasswordInput)


    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    def clean_password2(self):
        cleaned_data = self.changed_data
        if cleaned_data['password'] != cleaned_data['password2']:
            raise forms.ValidationError('Hasła nie są identyczne')
        return cleaned_data['password2']