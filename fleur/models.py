from django.db import models

class Distributor(models.Model):
    name = models.CharField(max_length=120)
    serial_number = models.CharField(max_length=64, unique=True)
    location = models.CharField(max_length=255, blank=True)
    is_online = models.BooleanField(default=False)
    firmware = models.CharField(max_length=64, blank=True)
    last_heartbeat = models.DateTimeField(null=True, blank=True)
    def __str__(self): return f"{self.name} ({self.serial_number})"

class Slot(models.Model):
    BIG="BIG"; LOCKER="LOCKER"
    TYPES=[(BIG,"Grande porte"),(LOCKER,"Casier")]
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE, related_name="slots")
    code = models.CharField(max_length=10)               # D1/D2/L1..L6
    relay_channel = models.PositiveIntegerField()        # canal sur la carte driver
    door_type = models.CharField(max_length=10, choices=TYPES, default=LOCKER)
    capacity = models.PositiveIntegerField(default=1)
    quantity = models.PositiveIntegerField(default=1)
    is_enabled = models.BooleanField(default=True)

    class Meta:
        unique_together = [("distributor","code")]

    def __str__(self): return f"{self.distributor.serial_number}:{self.code}"

class Order(models.Model):
    PENDING="PENDING"; PAID="PAID"; VENDED="VENDED"; FAILED="FAILED"
    STATUSES=[(PENDING,"En attente"),(PAID,"Payé"),(VENDED,"Vendu"),(FAILED,"Échec")]
    distributor = models.ForeignKey(Distributor, on_delete=models.PROTECT)
    slot = models.ForeignKey(Slot, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUSES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

class VendEvent(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="events")
    event = models.CharField(max_length=30)              # PAYMENT_OK, OPEN_OK, ...
    payload = models.JSONField(default=dict, blank=True)
    ts = models.DateTimeField(auto_now_add=True)


class HomeVideo(models.Model):
    """
    Une seule vidéo “active” suffit. On prend la plus récente pour la page d’accueil.
    """
    file = models.FileField(upload_to="home_videos/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"HomeVideo #{self.pk}"
