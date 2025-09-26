import json
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET

from .forms import DataUploadForm, UserProfileForm
from .models import UserProfile

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

# ------------------ Views existentes ------------------

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

# ------------------ Perfil do usuário (URN por usuário) ------------------

@login_required
def profile_settings(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = UserProfileForm(request.POST)
        if form.is_valid():
            profile.aps_urn = form.cleaned_data["aps_urn"].strip()
            profile.tandem_project_id = form.cleaned_data["tandem_project_id"].strip()
            profile.tandem_twin_id = form.cleaned_data["tandem_twin_id"].strip()
            profile.save()
            messages.success(request, "Perfil atualizado.")
            return redirect("core:profile")
        else:
            messages.error(request, "Verifique os campos.")
    else:
        form = UserProfileForm(initial={
            "aps_urn": profile.aps_urn,
            "tandem_project_id": profile.tandem_project_id,
            "tandem_twin_id": profile.tandem_twin_id,
        })
    return render(request, "profile.html", {"form": form})

# ------------------ Viewer Tandem/APS ------------------

@login_required
def viewer(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, "viewer.html", {
        "aps_urn": profile.aps_urn,          # URN do usuário logado
        "aps_region": settings.APS_REGION,   # US/EMEA
    })

# ------------------ Token APS (2-legged) ------------------

@login_required
@require_GET
def aps_token(request):
    """
    Endpoint seguro que troca client_id/secret por access_token (data:read/viewables:read).
    O segredo NUNCA vai para o frontend — só o token resultante.
    """
    cid = settings.APS_CLIENT_ID
    csec = settings.APS_CLIENT_SECRET
    scopes = settings.APS_SCOPES

    if not cid or not csec:
        return JsonResponse({"error": "APS credentials missing"}, status=500)

    data = {
        "grant_type": "client_credentials",
        "client_id": cid,
        "client_secret": csec,
        "scope": scopes,
    }

    # endpoint OAuth APS
    token_url = "https://developer.api.autodesk.com/authentication/v2/token"

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(token_url, data=data)
            resp.raise_for_status()
            payload = resp.json()
            # retorna somente o necessário ao viewer
            return JsonResponse({
                "access_token": payload.get("access_token"),
                "expires_in": payload.get("expires_in", 1800),
                "token_type": payload.get("token_type", "Bearer"),
            })
    except httpx.HTTPError as e:
        return JsonResponse({"error": f"APS token error: {e}"}, status=502)
