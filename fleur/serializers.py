from rest_framework import serializers
from .models import Distributor, Slot, Order, VendEvent

class DistributorSerializer(serializers.ModelSerializer):
    class Meta: model = Distributor; fields = "__all__"

class SlotSerializer(serializers.ModelSerializer):
    class Meta: model = Slot; fields = "__all__"

class VendEventSerializer(serializers.ModelSerializer):
    class Meta: model = VendEvent; fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):
    events = VendEventSerializer(many=True, read_only=True)
    class Meta: model = Order; fields = "__all__"
