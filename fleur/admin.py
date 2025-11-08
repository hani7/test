from django.contrib import admin
from .models import Distributor, Slot, Order, VendEvent

class SlotInline(admin.TabularInline):
    model = Slot
    extra = 0

@admin.register(Distributor)
class DistributorAdmin(admin.ModelAdmin):
    list_display=("name","serial_number","location","is_online","last_heartbeat")
    inlines=[SlotInline]

@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display=("distributor","code","relay_channel","door_type","quantity","is_enabled")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display=("id","distributor","slot","amount","status","created_at")
    list_filter=("status",)

@admin.register(VendEvent)
class VendEventAdmin(admin.ModelAdmin):
    list_display=("order","event","ts")
