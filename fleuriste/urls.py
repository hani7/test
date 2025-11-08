from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from fleur.api import DistributorViewSet, SlotViewSet, OrderViewSet, HealthView

router = DefaultRouter()
router.register("distributors", DistributorViewSet)
router.register("slots", SlotViewSet)
router.register("orders", OrderViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/health/", HealthView.as_view()),
    path("", include("fleur.urls")),

]
