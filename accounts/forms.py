from ctypes import resize
from django import forms
from django.contrib.auth import get_user_model, login, authenticate
from django.forms import PasswordInput
from .models import Profile

User = get_user_model()


class RegistrationForm(forms.ModelForm):
    username = forms.CharField(help_text="")
    age = forms.IntegerField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username", "age", "email", "first_name", "last_name", "password1", "password2")


    def clean(self, *args, **kwargs):
        super(RegistrationForm, self).clean(*args, **kwargs)

        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        age = self.cleaned_data.get("age")
        email = self.cleaned_data.get("email")

        user_qs = User.objects.filter(email=email).exists()

        if password1 != password2:
            raise forms.ValidationError("Şifrələr uyğunlaşmır")

        if age < 18:
            raise forms.ValidationError("Balacalar bura daxil ola bilməz")

        if user_qs:
            raise forms.ValidationError("Bu email ilə qeydiyyatdan keçilib")



    def save(self, *args, **kwargs):
        cleaned_data = self.cleaned_data

        username = cleaned_data.get("username")
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")
        email = cleaned_data.get("email")
        password1 = cleaned_data.get("password1")
        age = cleaned_data.get("age")

        user = User.objects.create(
            username=username, first_name=first_name, last_name=last_name,
            email=email
        )
        user.set_password(password1)
        user.save()

        Profile.objects.create(
            user=user, age=age
        )

        # first authenticate

        new_user = authenticate(username=username, password=password1)

        return user


class LoginForm(forms.Form):
    username = forms.CharField(help_text="")
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        super(LoginForm, self).clean(*args, **kwargs)
        cleaned_data = self.cleaned_data

        # cleaned_data = super(LoginForm, self).clean(*args, **kwargs)

        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        user = authenticate(username=username, password=password)

        if user:

            if not user.check_password(password):
                raise forms.ValidationError("Şifrə yalnışdır")

            if not user.is_active:
                raise forms.ValidationError("Bu istifadəçi aktiv deyil")
        else:
            raise forms.ValidationError("Bu istifadəçi mövcud deyil")

    def save(self, *args, **kwargs):
        cleaned_data = self.cleaned_data

        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        user = authenticate(username=username, password=password)
        return user



