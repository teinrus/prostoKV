from django.contrib import admin

from temruk.admin import TNR_admin_site
from .models import *

TNR_admin_site.register(Table31)
TNR_admin_site.register(Speed31)
TNR_admin_site.register(ProductionOutput31)

TNR_admin_site.register(Table33)
TNR_admin_site.register(Speed33)
TNR_admin_site.register(ProductionOutput33)

TNR_admin_site.register(Table24)
TNR_admin_site.register(Speed24)
TNR_admin_site.register(ProductionOutput24)

TNR_admin_site.register(Table25)
TNR_admin_site.register(Speed25)
TNR_admin_site.register(ProductionOutput25)

TNR_admin_site.register(Table26)
TNR_admin_site.register(Speed26)
TNR_admin_site.register(ProductionOutput26)


TNR_admin_site.register(ProductionTime31)
TNR_admin_site.register(ProductionTime33)

