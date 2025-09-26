import json
from pathlib import Path
from django.conf import settings
from django.urls import reverse_lazy         # ⬅️ importe isto
from django.shortcuts import resolve_url
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.views.generic import FormView
from .forms import DataUploadForm, EmailOrUsernameAuthenticationForm

ATIVOS_PATH = Path(settings.BASE_DIR) / "ativos.json"

def load_assets():
    if ATIVOS_PATH.exists():
        try:
            with open(ATIVOS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "ativos" in data:
                    return data["ativos"]
                return data
        except Exception:
            return []
    return []

def filter_assets(assets, q: str):
    if not q:
        return assets
    q = q.lower()
    def match(a):
        texto = json.dumps(a, ensure_ascii=False).lower()
        return q in texto
    return [a for a in assets if match(a)]

# --------- AUTH ---------

class LoginViewCustom(FormView):
    template_name = "registration/login.html"
    form_class = EmailOrUsernameAuthenticationForm
    # transforme o nome da rota em URL preguiçosa:
    success_url = reverse_lazy("core:dashboard")   # ⬅️ aqui

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        if not form.cleaned_data.get("remember_me"):
            self.request.session.set_expiry(0)
        messages.success(self.request, "Bem-vindo(a) de volta!")
        return super().form_valid(form)

    # (opcional, para honrar ?next=)
    def get_success_url(self):
        redirect_to = self.request.POST.get("next") or self.request.GET.get("next")
        if redirect_to and url_has_allowed_host_and_scheme(
            redirect_to, allowed_hosts={self.request.get_host()}
        ):
            return redirect_to
        return super().get_success_url()

def logout_view(request):
    logout(request)
    messages.info(request, "Você saiu da sessão.")
    return redirect(settings.LOGOUT_REDIRECT_URL)

# --------- VIEWS PROTEGIDAS ---------

@login_required
def dashboard(request):
    q = request.GET.get("q", "")
    assets = filter_assets(load_assets(), q)
    upload_form = DataUploadForm()
    context = {
        "q": q,
        "assets": assets[:12],
        "total": len(assets),
        "upload_form": upload_form,
    }
    return render(request, "dashboard.html", context)

@login_required
def asset_list_partial(request):
    q = request.GET.get("q", "")
    page = int(request.GET.get("page", "1"))
    page_size = 12

    assets = filter_assets(load_assets(), q)
    start = (page - 1) * page_size
    end = start + page_size
    context = {
        "assets": assets[start:end],
        "page": page,
        "has_more": end < len(assets),
        "q": q,
    }
    return render(request, "_asset_cards.html", context)

@login_required
def upload_file(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Método inválido.")
    form = DataUploadForm(request.POST, request.FILES)
    if form.is_valid():
        f = form.cleaned_data["arquivo"]
        media_dir = settings.MEDIA_ROOT
        Path(media_dir).mkdir(parents=True, exist_ok=True)
        dest = Path(media_dir) / f.name
        with open(dest, "wb+") as destf:
            for chunk in f.chunks():
                destf.write(chunk)
        messages.success(request, "Arquivo enviado com sucesso.")
        return redirect("core:dashboard")
    messages.error(request, "Falha no envio do arquivo.")
    return redirect("core:dashboard")
