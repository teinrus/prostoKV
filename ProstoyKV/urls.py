from django.contrib import admin
from django.urls import path, include
from temruk.admin import TNR_admin_site


urlpatterns = [
    path('', include('temruk.urls')),
    path('titorovka/', include('titorovka.urls')),

    path("admin/", TNR_admin_site.urls),
    path('accounts/',include("django.contrib.auth.urls"))
]