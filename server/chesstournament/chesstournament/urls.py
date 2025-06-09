from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # Primero se incluyen las rutas personalizadas de la API
    path("api/v1/", include("api.urls")),
    # Luego las rutas de Djoser y del token
    # path("api/v1/", include("djoser.urls")),
    path("api/v1/", include("djoser.urls.authtoken")),
]
