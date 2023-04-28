from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('temruk.urls')),
    path('admin/', admin.site.urls, name='admin'),
    path('accounts/',include("django.contrib.auth.urls")),
    path('titorovka/', include('titorovka.urls'))
]