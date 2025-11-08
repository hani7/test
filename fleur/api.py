import requests
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Distributor, Slot, Order, VendEvent
from .serializers import DistributorSerializer, SlotSerializer, OrderSerializer

class DistributorViewSet(viewsets.ModelViewSet):
    queryset = Distributor.objects.all()
    serializer_class = DistributorSerializer

class SlotViewSet(viewsets.ModelViewSet):
    queryset = Slot.objects.all()
    serializer_class = SlotSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by("-id")
    serializer_class = OrderSerializer

    @action(detail=True, methods=["post"])
    def vend(self, request, pk=None):
        order: Order = self.get_object()
        slot: Slot = order.slot

        # (démo) marquer payé si PENDING
        if order.status == Order.PENDING:
            order.status = Order.PAID
            order.save()
            VendEvent.objects.create(order=order, event="PAYMENT_OK")

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
            order.status = Order.VENDED
            order.save()
            VendEvent.objects.create(order=order, event="OPEN_OK", payload={"relay_channel": slot.relay_channel})
            if slot.quantity > 0:
                slot.quantity -= 1; slot.save()
            return Response({"ok": True, "status": order.status})

        order.status = Order.FAILED
        order.save()
        VendEvent.objects.create(order=order, event="OPEN_FAIL", payload={"relay_channel": slot.relay_channel})
        return Response({"ok": False, "status": order.status}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HealthView(APIView):
    def get(self, request):
        return Response({"status":"ok"})
