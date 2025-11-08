from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.views.decorators.http import require_http_methods
import requests

from .forms import HomeVideoForm
from .models import HomeVideo, Slot, Order, VendEvent
from django.contrib import messages as dj_messages

def home(request):
    """
    Affiche la dernière vidéo + formulaire d’upload (optionnel).
    Bouton Start => bouquets.
    """
    last_video = HomeVideo.objects.order_by("-uploaded_at").first()
    form = HomeVideoForm()

    if request.method == "POST":
        form = HomeVideoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("home")

    return render(request, "fleur/home.html", {"video": last_video, "form": form})

def bouquets(request):
    """
    Liste des casiers/portes disponibles (quantity>0 et is_enabled).
    """
    slots = Slot.objects.filter(is_enabled=True).order_by("relay_channel")
    return render(request, "fleur/bouquets.html", {"slots": slots})

@require_http_methods(["POST"])
def buy_now(request, slot_id):
    """
    Crée une commande PENDING pour le slot choisi puis redirige vers /pay/<order_id>/
    """
    slot = get_object_or_404(Slot, pk=slot_id, is_enabled=True)
    # Prix démo: 1000 DA — adapte selon ton modèle
    order = Order.objects.create(distributor=slot.distributor, slot=slot, amount="1000.00")
    return redirect("pay", order_id=order.id)

def pay(request, order_id):
    """
    Page paiement simple (démo). POST = “payer maintenant” :
    - marque payé
    - appelle l’endpoint /api/orders/<id>/vend/ (ouvrira la porte via l’agent)
    - redirige vers success/ ou échec
    """
    order = get_object_or_404(Order, pk=order_id)

    if request.method == "POST":
        # Simule un paiement OK (à remplacer par ton PSP ou acceptateur billets)
        if order.status == Order.PENDING:
            order.status = Order.PAID
            order.save()
            VendEvent.objects.create(order=order, event="PAYMENT_OK")

        # Appelle l’API interne pour déclencher l’ouverture
        base = request.build_absolute_uri("/")[:-1]  # ex. http://localhost:8000
        try:
            r = requests.post(f"{base}/api/orders/{order.id}/vend/", timeout=6)
            ok = r.ok and r.json().get("ok") is True
        except Exception:
            ok = False

        if ok:
            return redirect("pay_success", order_id=order.id)
        else:
            return redirect("pay_failed", order_id=order.id)

    return render(request, "fleur/pay.html", {"order": order})

def pay_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, "fleur/pay_success.html", {"order": order})

def pay_failed(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, "fleur/pay_failed.html", {"order": order})


from .models import Slot

@require_http_methods(["POST"])
def open_door(request, slot_id):
    slot = get_object_or_404(Slot, pk=slot_id, is_enabled=True)
    agent = settings.AGENT_BASE_URL.rstrip("/")
    ok = False
    try:
        r = requests.post(f"{agent}/open",
                          params={"slot": slot.relay_channel, "duration_ms": 600},
                          timeout=5)
        ok = r.ok and r.json().get("ok") is True
    except Exception:
        ok = False

    if ok:
        dj_messages.success(request, f"Porte {slot.code} ouverte.")
    else:
        dj_messages.error(request, f"Échec ouverture {slot.code}.")
    return redirect("bouquets")


@require_http_methods(["POST"])
def open_both_big(request):
    big_doors = list(Slot.objects.filter(door_type="BIG", is_enabled=True).order_by("relay_channel")[:2])
    agent = settings.AGENT_BASE_URL.rstrip("/")
    opened, failed = [], []

    for s in big_doors:
        ok = False
        try:
            r = requests.post(f"{agent}/open",
                              params={"slot": s.relay_channel, "duration_ms": 600},
                              timeout=5)
            ok = r.ok and r.json().get("ok") is True
        except Exception:
            ok = False
        (opened if ok else failed).append(s.code)

    if opened:
        dj_messages.success(request, f"Porte(s) ouverte(s) : {', '.join(opened)}.")
    if failed:
        dj_messages.error(request, f"Échec : {', '.join(failed)}.")
    return redirect("bouquets")


@require_http_methods(["POST"])
def open_all_lockers(request):
    lockers = list(Slot.objects.filter(door_type="LOCKER", is_enabled=True).order_by("relay_channel"))
    agent = settings.AGENT_BASE_URL.rstrip("/")
    opened, failed = [], []

    for s in lockers:
        ok = False
        try:
            r = requests.post(f"{agent}/open",
                              params={"slot": s.relay_channel, "duration_ms": 600},
                              timeout=5)
            ok = r.ok and r.json().get("ok") is True
        except Exception:
            ok = False
        (opened if ok else failed).append(s.code)

    if opened:
        dj_messages.success(request, f"Casiers ouverts : {', '.join(opened)}.")
    if failed:
        dj_messages.error(request, f"Échec : {', '.join(failed)}.")
    return redirect("bouquets")