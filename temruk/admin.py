from django.contrib import admin
from django.contrib.admin import AdminSite

# Register your models here.
from .models import *

class CustomAdminSite(AdminSite):
    site_header = "Панель администратора АСУПростоев"
    site_title = "TNR"
    index_title = "TNR проект для 'Кубань Вино'"
    site_logo = "images/logo.png"


TNR_admin_site = CustomAdminSite(name="customadmin")




TNR_admin_site.register(Table2)
TNR_admin_site.register(Speed2)

TNR_admin_site.register(Table4)
TNR_admin_site.register(Speed4)

TNR_admin_site.register(Table5)
TNR_admin_site.register(Speed5)
TNR_admin_site.register(CO2_Rozliv)

TNR_admin_site.register(ProductionOutput1)
TNR_admin_site.register(ProductionOutput2)
TNR_admin_site.register(ProductionOutput4)
TNR_admin_site.register(ProductionOutput5)


TNR_admin_site.register(prichina)
TNR_admin_site.register(uchastok)

TNR_admin_site.register(bottleExplosion5)

TNR_admin_site.register(bottling_plan)
TNR_admin_site.register(Nomenclature)
TNR_admin_site.register(Line)

TNR_admin_site.register(NapAcratofori)
TNR_admin_site.register(Line5Indicators)
TNR_admin_site.register(Line2Indicators)


