from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("bouquets/", views.bouquets, name="bouquets"),
    path("buy/<int:slot_id>/", views.buy_now, name="buy_now"),
    path("pay/<int:order_id>/", views.pay, name="pay"),
    path("pay/<int:order_id>/success/", views.pay_success, name="pay_success"),
    path("pay/<int:order_id>/failed/", views.pay_failed, name="pay_failed"),

        # Nouveaux endpoints maintenance:
    path("open/<int:slot_id>/", views.open_door, name="open_door"),
    path("open/both-big/", views.open_both_big, name="open_both_big"),
    path("open/lockers/", views.open_all_lockers, name="open_all_lockers"),  # ← NEW

]
