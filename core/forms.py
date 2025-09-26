from django import forms
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()

class DataUploadForm(forms.Form):
    arquivo = forms.FileField(
        label="Enviar arquivo (CSV/JSON)",
        help_text="Carregue dados do gêmeo digital"
    )

class EmailOrUsernameAuthenticationForm(forms.Form):
    username = forms.CharField(
        label="Usuário ou e-mail",
        widget=forms.TextInput(attrs={"autocomplete": "username"})
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"})
    )
    remember_me = forms.BooleanField(
        label="Manter conectado",
        required=False,
        initial=True
    )

    def __init__(self, *args, **kwargs):
        self._user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        username_or_email = cleaned.get("username")
        password = cleaned.get("password")
        if not username_or_email or not password:
            raise forms.ValidationError("Informe usuário/e-mail e senha.")

        # tenta autenticar por username primeiro
        user = authenticate(username=username_or_email, password=password)
        if user is None:
            # tenta por e-mail
            try:
                u = User.objects.get(email__iexact=username_or_email)
                user = authenticate(username=u.get_username(), password=password)
            except User.DoesNotExist:
                user = None

        if user is None:
            raise forms.ValidationError("Credenciais inválidas.")
        if not user.is_active:
            raise forms.ValidationError("Conta inativa.")
        self._user = user
        return cleaned

    def get_user(self):
        return self._user
