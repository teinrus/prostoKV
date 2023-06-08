import datetime


from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from django.db.models import Sum, Avg
from django.http import HttpResponse

from django.shortcuts import render, redirect

from temruk.models import *

from .forms import Otchet
from  pyModbusTCP.client import ModbusClient




def mod_bus(reg,bit_temp):

    slave_address = '192.168.88.230'
    port = 502
    unit_id = 1
    modbus_client = ModbusClient(host=slave_address, port=port, unit_id=unit_id, auto_open=True)
    test = modbus_client.write_single_register(reg, bit_temp)



start1 = datetime.time(8, 00, 0)
start2 = datetime.time(16, 30, 0)
start3 = datetime.time(23, 59, 0)

if start1 <= datetime.datetime.now().time() <= start2:
    startSmena = datetime.time(8, 00, 0)
    spotSmena = datetime.time(16, 30, 0)
elif start2 <= datetime.datetime.now().time() <= start3:
    startSmena = datetime.time(16, 30, 0)
    spotSmena = datetime.time(23, 59, 0)
else:
    startSmena = datetime.time(00, 00, 00)
    spotSmena = datetime.time(8, 00, 00)

# функция формирования процентов за текущию смену
def proc(startSmena, spotSmena, plan, colProduct):
    today = datetime.date.today()
    # количество продукции вып в сек
    d_start1 = datetime.datetime.combine(today, startSmena)
    d_end1 = datetime.datetime.combine(today, spotSmena)
    diff1 = d_end1 - d_start1
    planProdSec = int(plan / int(diff1.total_seconds()))

    # количество времени которое прошло
    d_start2 = datetime.datetime.combine(today, startSmena)
    d_end2 = datetime.datetime.combine(today, datetime.datetime.now().time())
    diff2 = d_end2 - d_start2

    # проц вып продукции
    return int(colProduct / ((int(diff2.total_seconds()) * planProdSec) / 100))

# стартовая страница
def index(request):
    if request.method == 'GET':
        user_ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if user_ip:
            ip = user_ip.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
    ipMask=ip.split('.')
    if ipMask[2] =="97":
        return redirect('temruk')
    else:
        return redirect('titorovka')



def temruk(request):
    if request.method == 'GET':
        table5 = Table5.objects.filter(startdata=datetime.date.today(),
                                      starttime__gte=startSmena,
                                      starttime__lte=spotSmena)
        speed5 = Speed5.objects.filter(data=datetime.date.today(),
                                      time__gte=startSmena,
                                      time__lte=spotSmena)
        table4 = Table4.objects.filter(startdata=datetime.date.today(),
                                      starttime__gte=startSmena,
                                      starttime__lte=spotSmena)
        speed4 = Speed4.objects.filter(data=datetime.date.today(),
                                      time__gte=startSmena,
                                      time__lte=spotSmena)
        table2 = Table2.objects.filter(startdata=datetime.date.today(),
                                       starttime__gte=startSmena,
                                       starttime__lte=spotSmena)
        speed2 = Speed2.objects.filter(data=datetime.date.today(),
                                       time__gte=startSmena,
                                       time__lte=spotSmena)

    prichAll=prichina.objects.all()
    podrazdeleniaEl=[]
    for el in prichAll:
        podrazdeleniaEl.append(el.key)
    otv_p=set(podrazdeleniaEl)

    prich = list(prichAll.values())
    uch = uchastok.objects.all()
    uch_vino=uchastok.objects.exclude(uchastok="Мюзле")
    return render(request, "temruk.html", {

        'otv_p':otv_p ,
        'prich': prich,
        'uch': uch,
        'uch_vino': uch_vino,

        'table5': table5,
        'speed5': speed5,

        'table4': table4,
        'speed4': speed4,

        'table2': table2,
        'speed2': speed2,

    })

def start_perenaladka5(request):
    mod_bus(0,1)
    return HttpResponse('yes')
def start_donaladka5(request):
    mod_bus(0,2)
    return HttpResponse('yes')

def rabota5(request):
    mod_bus(0,4)
    return HttpResponse('yes')
def TO5(request):
    mod_bus(0,8)
    return HttpResponse('yes')

def start_perenaladka4(request):
    mod_bus(1,1)
    return HttpResponse('yes')
def start_donaladka4(request):
    mod_bus(1,2)
    return HttpResponse('yes')

def rabota4(request):
    mod_bus(1,4)
    return HttpResponse('yes')
def TO4(request):
    mod_bus(1,8)
    return HttpResponse('yes')

def start_perenaladka2(request):
    mod_bus(2,1)
    return HttpResponse('yes')
def start_donaladka2(request):
    mod_bus(2,2)
    return HttpResponse('yes')

def rabota2(request):
    mod_bus(2,4)
    return HttpResponse('yes')
def TO2(request):
    mod_bus(2,8)
    return HttpResponse('yes')



# блок формирования отчета
def otchet(request):
    plan=0
    table=[]
    timeTemp = 0
    form = Otchet(request.GET)
    if form.is_valid():
        # Сортировка по дате
        if form.cleaned_data["start_data"] and form.cleaned_data["finish_data"] and (
                form.cleaned_data["LineF"] == 'Линиия 5'):
            if form.cleaned_data["SmenaF"]:
                if form.cleaned_data["SmenaF"] == 'Смена 0':
                    table = Table5.objects.filter(starttime__gte=datetime.time(0),
                                                  starttime__lte=datetime.time(23, 59),
                                                  startdata__gte=form.cleaned_data["start_data"],
                                                  startdata__lte=form.cleaned_data["finish_data"]
                                                  ).order_by('startdata', 'starttime')

                    speed = Speed5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(0),
                                                  time__lte=datetime.time(23, 59))
                    boom = bottleExplosion5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                          data__lte=form.cleaned_data["finish_data"],
                                                          time__gte=datetime.time(0),
                                                          time__lte=datetime.time(23, 59))
                    prod = ProductionOutput5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(0),
                                                  time__lte=datetime.time(23, 59))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='22b8afd6-110a-11e6-b0ff-005056ac2c77',
                                                            )
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0

                    try:
                        timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data[
                            "start_data"] + datetime.timedelta(days=1)



                    except:
                        timeTemp = 0

                if form.cleaned_data["SmenaF"] == 'Смена 1':
                    table = Table5.objects.filter(starttime__gte=datetime.time(8),
                                                  starttime__lte=datetime.time(16, 30),
                                                  startdata__gte=form.cleaned_data["start_data"],
                                                  startdata__lte=form.cleaned_data["finish_data"]
                                                  ).order_by('startdata', 'starttime')
                    speed = Speed5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(8),
                                                  time__lte=datetime.time(16, 30))
                    boom = bottleExplosion5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                          data__lte=form.cleaned_data["finish_data"],
                                                          time__gte=datetime.time(8),
                                                          time__lte=datetime.time(16, 30))
                    prod = ProductionOutput5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(8),
                                                  time__lte=datetime.time(16, 30))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='22b8afd6-110a-11e6-b0ff-005056ac2c77',
                                                            ShiftNumber=1)
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0

                    try:
                        timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                        count=1+timeTemp.total_seconds()/3600/24
                        timeTemp=datetime.timedelta(hours=(8*count),minutes=30*count)
                    except:
                        timeTemp = 0
                if form.cleaned_data["SmenaF"] == 'Смена 2':
                    table = Table5.objects.filter(starttime__gte=datetime.time(16, 30),
                                                  starttime__lte=datetime.time(23, 59),
                                                  startdata__gte=form.cleaned_data["start_data"],
                                                  startdata__lte=form.cleaned_data["finish_data"]
                                                  ).order_by('startdata', 'starttime')
                    speed = Speed5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(16, 30),
                                                  time__lte=datetime.time(23, 59))
                    boom = bottleExplosion5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                          data__lte=form.cleaned_data["finish_data"],
                                                          time__gte=datetime.time(16, 30),
                                                          time__lte=datetime.time(23, 59))
                    prod = ProductionOutput5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(16, 30),
                                                  time__lte=datetime.time(23, 59))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='22b8afd6-110a-11e6-b0ff-005056ac2c77',
                                                            ShiftNumber=2)
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0

                    try:
                        timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                        count=timeTemp.total_seconds()/3600/24+1

                        timeTemp=datetime.timedelta(hours=(7*count),minutes=30*count)
                    except:
                        timeTemp = 0
                if form.cleaned_data["SmenaF"] == 'Смена 3':
                    table = Table5.objects.filter(starttime__gte=datetime.time(00, 00),
                                                  starttime__lte=datetime.time(8, 00),
                                                  startdata__gte=form.cleaned_data["start_data"],
                                                  startdata__lte=form.cleaned_data["finish_data"]
                                                  ).order_by('startdata', 'starttime')
                    speed = Speed5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(00, 00),
                                                  time__lte=datetime.time(8, 00))
                    boom = bottleExplosion5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                          data__lte=form.cleaned_data["finish_data"],
                                                          time__gte=datetime.time(00, 00),
                                                          time__lte=datetime.time(8, 00))
                    prod = ProductionOutput5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(00, 00),
                                                  time__lte=datetime.time(8, 00))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='22b8afd6-110a-11e6-b0ff-005056ac2c77',
                                                            ShiftNumber=3)
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0

                    try:
                        timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                        count=timeTemp.total_seconds()/3600/24+1

                        timeTemp=datetime.timedelta(hours=(8*count))
                    except:
                        timeTemp = 0
        # Сортировка по сменам линии 2:
        if form.cleaned_data["start_data"] and form.cleaned_data["finish_data"] and (
                form.cleaned_data["LineF"] == 'Линиия 2'):
            if form.cleaned_data["SmenaF"]:
                if form.cleaned_data["SmenaF"] == 'Смена 0':
                    table2 = Table2.objects.filter(starttime__gte=datetime.time(0),
                                                   starttime__lte=datetime.time(23, 59),
                                                   startdata__gte=form.cleaned_data["start_data"],
                                                   startdata__lte=form.cleaned_data["finish_data"]
                                                   ).order_by('startdata', 'starttime')

                    speed2 = Speed2.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                   data__lte=form.cleaned_data["finish_data"],
                                                   time__gte=datetime.time(0),
                                                   time__lte=datetime.time(23, 59))
                    productionOutput2 = ProductionOutput2.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                   data__lte=form.cleaned_data["finish_data"],
                                                   time__gte=datetime.time(0),
                                                   time__lte=datetime.time(23, 59))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='48f7e8d8-1114-11e6-b0ff-005056ac2c77')
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0

                    try:
                        timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data[
                            "start_data"] + datetime.timedelta(days=1)
                    except:
                        timeTemp = 0
            if form.cleaned_data["SmenaF"] == 'Смена 1':
                table2 = Table2.objects.filter(starttime__gte=datetime.time(8),
                                               starttime__lte=datetime.time(16, 30),
                                               startdata__gte=form.cleaned_data["start_data"],
                                               startdata__lte=form.cleaned_data["finish_data"]
                                               ).order_by('startdata', 'starttime')
                speed2 = Speed2.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(8),
                                               time__lte=datetime.time(16, 30))
                productionOutput2 = ProductionOutput2.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(8),
                                               time__lte=datetime.time(16, 30))
                try:
                    plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                        Data__lte=form.cleaned_data["finish_data"],
                                                        GIUDLine='48f7e8d8-1114-11e6-b0ff-005056ac2c77',
                                                        ShiftNumber=1)
                    plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                except:
                    plan=0
                try:

                    timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                    count = timeTemp.total_seconds() / 3600 / 24 + 1

                    timeTemp = datetime.timedelta(hours=(8*count),minutes=30*count)
                except:
                    timeTemp = 0
            if form.cleaned_data["SmenaF"] == 'Смена 2':
                table2 = Table2.objects.filter(starttime__gte=datetime.time(16, 30),
                                               starttime__lte=datetime.time(23, 59),
                                               startdata__gte=form.cleaned_data["start_data"],
                                               startdata__lte=form.cleaned_data["finish_data"]
                                               ).order_by('startdata', 'starttime')
                speed2 = Speed2.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(16, 30),
                                               time__lte=datetime.time(23, 59))
                productionOutput2 = ProductionOutput2.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(16, 30),
                                               time__lte=datetime.time(23, 59))
                try:
                    plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                        Data__lte=form.cleaned_data["finish_data"],
                                                        GIUDLine='48f7e8d8-1114-11e6-b0ff-005056ac2c77',
                                                        ShiftNumber=2)
                    plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                except:
                    plan=0

                try:

                    timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                    count = timeTemp.total_seconds() / 3600 / 24 + 1

                    timeTemp = datetime.timedelta(hours=(7*count),minutes=30*count)
                except:
                    timeTemp = 0


            if form.cleaned_data["SmenaF"] == 'Смена 3':
                table2 = Table2.objects.filter(starttime__gte=datetime.time(00, 00),
                                               starttime__lte=datetime.time(8, 00),
                                               startdata__gte=form.cleaned_data["start_data"],
                                               startdata__lte=form.cleaned_data["finish_data"]
                                               ).order_by('startdata', 'starttime')
                speed2 = Speed2.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(00, 00),
                                               time__lte=datetime.time(8, 00))
                productionOutput2 = ProductionOutput2.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(00, 00),
                                               time__lte=datetime.time(8, 00))
                try:
                    plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                        Data__lte=form.cleaned_data["finish_data"],
                                                        GIUDLine='48f7e8d8-1114-11e6-b0ff-005056ac2c77',
                                                        ShiftNumber=3)
                    plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                except:
                    plan=0
                try:
                    timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                    count = timeTemp.total_seconds() / 3600 / 24 + 1

                    timeTemp = datetime.timedelta(hours=(8 * count))
                except:
                    timeTemp = 0

            table=table2
            speed=speed2
            prod=productionOutput2
            boom=0
        if form.cleaned_data["start_data"] and form.cleaned_data["finish_data"] and (
                form.cleaned_data["LineF"] == 'Линиия 4'):
            if form.cleaned_data["SmenaF"]:
                if form.cleaned_data["SmenaF"] == 'Смена 0':
                    table4 = Table4.objects.filter(starttime__gte=datetime.time(0),
                                                   starttime__lte=datetime.time(23, 59),
                                                   startdata__gte=form.cleaned_data["start_data"],
                                                   startdata__lte=form.cleaned_data["finish_data"]
                                                   ).order_by('startdata', 'starttime')

                    speed4 = Speed4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                   data__lte=form.cleaned_data["finish_data"],
                                                   time__gte=datetime.time(0),
                                                   time__lte=datetime.time(23, 59))
                    productionOutput4 = ProductionOutput4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                   data__lte=form.cleaned_data["finish_data"])


                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='b84d1e71-1109-11e6-b0ff-005056ac2c77')
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0
                    try:
                        timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data[
                            "start_data"] + datetime.timedelta(days=1)


                    except:
                        timeTemp = 0
            if form.cleaned_data["SmenaF"] == 'Смена 1':
                table4 = Table4.objects.filter(starttime__gte=datetime.time(8),
                                               starttime__lte=datetime.time(16, 30),
                                               startdata__gte=form.cleaned_data["start_data"],
                                               startdata__lte=form.cleaned_data["finish_data"]
                                               ).order_by('startdata', 'starttime')
                speed4 = Speed4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(8),
                                               time__lte=datetime.time(16, 30))
                productionOutput4 = ProductionOutput4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(8),
                                               time__lte=datetime.time(16, 30))
                try:
                    plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                        Data__lte=form.cleaned_data["finish_data"],
                                                        GIUDLine='b84d1e71-1109-11e6-b0ff-005056ac2c77',
                                                        ShiftNumber=1)
                    plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                except:
                    plan = 0
                try:
                    timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                    count = timeTemp.total_seconds() / 3600 / 24 + 1

                    timeTemp = datetime.timedelta(hours=(8*count),minutes=30*count)
                except:
                    timeTemp = 0
            if form.cleaned_data["SmenaF"] == 'Смена 2':
                table4 = Table4.objects.filter(starttime__gte=datetime.time(16, 30),
                                               starttime__lte=datetime.time(23, 59),
                                               startdata__gte=form.cleaned_data["start_data"],
                                               startdata__lte=form.cleaned_data["finish_data"]
                                               ).order_by('startdata', 'starttime')
                speed4 = Speed4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(16, 30),
                                               time__lte=datetime.time(23, 59))
                productionOutput4 = ProductionOutput4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(16, 30),
                                               time__lte=datetime.time(23, 59))
                try:
                    plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                        Data__lte=form.cleaned_data["finish_data"],
                                                        GIUDLine='b84d1e71-1109-11e6-b0ff-005056ac2c77',
                                                        ShiftNumber=2)
                    plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                except:
                    plan = 0
                try:
                    timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                    count = timeTemp.total_seconds() / 3600 / 24 + 1

                    timeTemp = datetime.timedelta(hours=(7*count),minutes=30*count)
                except:
                    timeTemp = 0


            if form.cleaned_data["SmenaF"] == 'Смена 3':
                table4 = Table4.objects.filter(starttime__gte=datetime.time(00, 00),
                                               starttime__lte=datetime.time(8, 00),
                                               startdata__gte=form.cleaned_data["start_data"],
                                               startdata__lte=form.cleaned_data["finish_data"]
                                               ).order_by('startdata', 'starttime')
                speed4 = Speed4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(00, 00),
                                               time__lte=datetime.time(8, 00))
                productionOutput4 = ProductionOutput4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(00, 00),
                                               time__lte=datetime.time(8, 00))
                try:
                    plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                        Data__lte=form.cleaned_data["finish_data"],
                                                        GIUDLine='b84d1e71-1109-11e6-b0ff-005056ac2c77',
                                                        ShiftNumber=3)
                    plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                except:
                    plan = 0
                try:
                    timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                    count = timeTemp.total_seconds() / 3600 / 24 + 1

                    timeTemp = datetime.timedelta(hours=(8 * count))
                except:
                    timeTemp = 0

            table=table4
            speed=speed4
            prod=productionOutput4
            boom=0
    lableChart = []
    dataChart = []

    #Общее количество  продукции
    try:
        allProd = prod.aggregate(Sum('production')).get('production__sum')
        if (allProd == None):
            allProd = 0
    except:
        allProd = 0


    #Общее количество  врывов бутылок
    try:
        boomOut = boom.aggregate(Sum('bottle')).get('bottle__sum')
        if (boomOut == None):
            boomOut = 0
    except:
        boomOut = 0

    #Общее время простоя
    try:
        sumProstoy = table.aggregate(Sum('prostoy')).get('prostoy__sum')
        if sumProstoy== None:
            sumProstoy=datetime.timedelta(0)
    except:
        sumProstoy = 0
    # Средняя скорость
    try:
        if sumProstoy>timeTemp:
            sumProstoy=timeTemp
        timeWork=(timeTemp -sumProstoy)


    except:
        timeWork=0
    try:
        avgSpeed =round((allProd / timeWork.total_seconds() * 3600),2)

    except:
        avgSpeed=0




    # Данные для графика

    try:
        for sp in speed:
            lableChart.append(str(sp.time))
            dataChart.append(sp.triblok)
    except:
        lableChart = []
        dataChart = []




    uch = uchastok.objects.all()
    uch_vino=uchastok.objects.exclude(uchastok="Мюзле")

    prichAll = prichina.objects.all()
    podrazdeleniaEl = []
    for el in prichAll:
        podrazdeleniaEl.append(el.key)
    otv_p = set(podrazdeleniaEl)

    prich = list(prichAll.values())

    line = form.cleaned_data["LineF"]
    smena=form.cleaned_data["SmenaF"]
    nachaloOt = form.cleaned_data["start_data"]
    okonchanieOt = form.cleaned_data["finish_data"]



    return render(request, "otchet.html", {
        'table': table,
        'form': form,


        'line':line,
        'smena':smena,
        'nachaloOt':nachaloOt,
        'okonchanieOt':okonchanieOt,

        'timeWork':timeWork,
        'plan':plan,
        'sumProstoy': sumProstoy,

        'avgSpeed': avgSpeed,


        'boomOut': boomOut,
        'allProd': allProd,

        'lableChart': lableChart,
        'dataChart': dataChart,

        'otv_p': otv_p,
        'prich': prich,
        'uch': uch,
        'uch_vino':uch_vino,



    })

def otchetSmena(request):
    nomenklatura=[]
    nomenklatura4=[]
    nomenklatura2=[]

    if  datetime.time(hour=8)< datetime.datetime.now().time()<datetime.time(hour=16,minute=30):
        print('3')
        smena=3
        start_data = datetime.datetime.today()
        finish_data = datetime.datetime.today()
        start_time = str(datetime.timedelta(hours=0))
        finish_time = str(datetime.timedelta(hours=8))
        timeTemp = datetime.timedelta(hours=8)
        dataTemp= datetime.datetime.today()


    elif datetime.datetime.now().time()>datetime.time(hour=16,minute=29):
        print('1')
        smena = 1
        start_data = datetime.datetime.today()
        finish_data = datetime.datetime.today()
        start_time = str(datetime.timedelta(hours=8))
        finish_time = str(datetime.timedelta(hours=16,minutes=30))
        timeTemp = datetime.timedelta(hours=8,minutes=30)
        dataTemp= datetime.datetime.today()
    else:
        print('2')
        smena = 2
        start_data = datetime.datetime.today()-datetime.timedelta(days=1)
        finish_data = datetime.datetime.today()-datetime.timedelta(days=1)
        start_time = str(datetime.timedelta(hours=16,minutes=30))
        finish_time = str(datetime.timedelta(hours=23,minutes=59))
        timeTemp = datetime.timedelta(hours=7, minutes=30)
        dataTemp= datetime.datetime.today()-datetime.timedelta(days=1)


    table5 = Table5.objects.filter(starttime__gte=start_time,
                                  starttime__lte=finish_time,
                                  startdata__gte=start_data,
                                  startdata__lte=finish_data
                                  ).order_by('startdata', 'starttime')
    table4 = Table4.objects.filter(starttime__gte=start_time,
                                  starttime__lte=finish_time,
                                  startdata__gte=start_data,
                                  startdata__lte=finish_data
                                  ).order_by('startdata', 'starttime')

    table2 = Table2.objects.filter(starttime__gte=start_time,
                                  starttime__lte=finish_time,
                                  startdata__gte=start_data,
                                  startdata__lte=finish_data
                                  ).order_by('startdata', 'starttime')

    boom5 = bottleExplosion5.objects.filter(data__gte=start_data,
                                           data__lte=finish_data,
                                           time__gte=start_time,
                                           time__lte=finish_time)
    boom5= boom5 if boom5 != None else 0


    prod5 = ProductionOutput5.objects.filter(data__gte=start_data,
                                  data__lte=finish_data,
                                  time__gte=start_time,
                                  time__lte=finish_time)
    prod4 = ProductionOutput4.objects.filter(data__gte=start_data,
                                  data__lte=finish_data,
                                  time__gte=start_time,
                                  time__lte=finish_time)
    prod2 = ProductionOutput2.objects.filter(data__gte=start_data,
                                  data__lte=finish_data,
                                  time__gte=start_time,
                                  time__lte=finish_time)

    speed=Speed5.objects.filter(data__gte=start_data,
                                  data__lte=finish_data,
                                  time__gte=start_time,
                                  time__lte=finish_time)
    speed4=Speed4.objects.filter(data__gte=start_data,
                                  data__lte=finish_data,
                                  time__gte=start_time,
                                  time__lte=finish_time)
    speed2=Speed2.objects.filter(data__gte=start_data,
                                  data__lte=finish_data,
                                  time__gte=start_time,
                                  time__lte=finish_time)
    try:
        plan = bottling_plan.objects.filter(Data__gte=start_data,
                                            Data__lte=finish_data,
                                            GIUDLine='22b8afd6-110a-11e6-b0ff-005056ac2c77',
                                            ShiftNumber= smena)

    except:
        plan = 0

    try:
        for el in plan:
            nomenklatura=Nomenclature.objects.filter(GUID=el.GUIDNomenсlature)
    except:
        nomenklatura= "План отсутствует"


    try:
        plan4 = bottling_plan.objects.filter(Data__gte=start_data,
                                            Data__lte=finish_data,
                                            GIUDLine='b84d1e71-1109-11e6-b0ff-005056ac2c77',
                                            ShiftNumber= smena)
    except:
        plan4 = 0

    try:
        for el in plan4:
            nomenklatura4=Nomenclature.objects.filter(GUID=el.GUIDNomenсlature)

    except:
        nomenklatura4= "План отсутствует"

    try:
        plan2 = bottling_plan.objects.filter(Data__gte=start_data,
                                            Data__lte=finish_data,
                                            GIUDLine='48f7e8d8-1114-11e6-b0ff-005056ac2c77',
                                            ShiftNumber= smena)
    except:
        plan2 = 0


    try:
        for el in plan2:
            print(el)
            nomenklatura2=Nomenclature.objects.filter(GUID=el.GUIDNomenсlature)

    except:
        nomenklatura2= "План отсутствует"



    #Общее количество  продукции
    try:
        allProd = prod5.aggregate(Sum('production')).get('production__sum')
        if (allProd == None):
            allProd = 0
        procent = int(allProd/plan.aggregate(Sum('Quantity')).get('Quantity__sum')*100)
    except:
        procent=0
        allProd = 0

    try:
        otklonenie=int(allProd) - int(plan.aggregate(Sum('Quantity')).get('Quantity__sum'))
    except:
        otklonenie=0

    try:
        allProd4 = prod4.aggregate(Sum('production')).get('production__sum')
        if (allProd4 == None):
            allProd4= 0
        procent4 =int( allProd4/plan4.aggregate(Sum('Quantity')).get('Quantity__sum') *100)

    except:
        allProd4 = 0
        procent4 = 0
    try:
        otklonenie4=int(allProd4) - int(plan4.aggregate(Sum('Quantity')).get('Quantity__sum'))
    except:
        otklonenie4=0
    try:
        allProd2 = prod2.aggregate(Sum('production')).get('production__sum')
        if (allProd2 == None):
            allProd2 = 0
        procent2 =int( allProd2/plan2.aggregate(Sum('Quantity')).get('Quantity__sum') *100)

    except:
        allProd2 = 0
        procent2=0
    try:
        otklonenie2=int(allProd2) - int(plan2.aggregate(Sum('Quantity')).get('Quantity__sum'))
    except:
        otklonenie2=0
    #Общее количество  врывов бутылок
    try:
        boomOut = boom5.aggregate(Sum('bottle')).get('bottle__sum')
        if (boomOut == None):
            boomOut = 0
    except:
        boomOut = 0

    #Общее время простоя
    try:
        sumProstoy = table5.aggregate(Sum('prostoy')).get('prostoy__sum')
        if sumProstoy== None:
            sumProstoy=datetime.timedelta(0)
    except:
        sumProstoy = 0
    try:
        sumProstoy4 = table4.aggregate(Sum('prostoy')).get('prostoy__sum')
        if sumProstoy4== None:
            sumProstoy4=datetime.timedelta(0)
    except:
        sumProstoy4 = 0
    try:
        sumProstoy2 = table2.aggregate(Sum('prostoy')).get('prostoy__sum')
        if sumProstoy2== None:
            sumProstoy2=datetime.timedelta(0)
    except:
        sumProstoy2 = 0

    # Средняя скорость
    try:
        if sumProstoy>timeTemp:
            sumProstoy=timeTemp
        timeWork=(timeTemp -sumProstoy)

    except:
        timeWork=0
    try:
        if sumProstoy4>timeTemp:
            sumProstoy4=timeTemp
        timeWork4=(timeTemp -sumProstoy4)

    except:
        timeWork4=0
    try:
        if sumProstoy2>timeTemp:
            sumProstoy2=timeTemp
        timeWork2=(timeTemp -sumProstoy2)

    except:
        timeWork2=0



    try:

        avgSpeed = round((allProd / timeWork.total_seconds() * 3600), 2)

    except:
        avgSpeed=0

    try:


        avgSpeed4=round((allProd4 / timeWork4.total_seconds() * 3600),2)

    except:
        avgSpeed4=0
    try:

        avgSpeed2 = round((allProd2 / timeWork2.total_seconds() * 3600), 2)
    except:
        avgSpeed2=0

    return render(request, "otchetSmena.html", {



        'otklonenie':otklonenie,
        'otklonenie4': otklonenie4,
        'otklonenie2': otklonenie2,


        'dataTemp':dataTemp.date(),
        'smena':smena,

        'procent':procent,
        'procent4': procent4,
        'procent2': procent2,


        'table5': table5,
        'table4': table4,
        'table2': table2,


        'timeWork':timeWork,
        'timeWork4': timeWork4,
        'timeWork2': timeWork2,

        'nomenklatura':     nomenklatura,
        'nomenklatura4':    nomenklatura4,
        'nomenklatura2':    nomenklatura2,

        'plan':             plan,
        'plan4':            plan4,
        'plan2':            plan2,

        'sumProstoy':       sumProstoy,
        'sumProstoy4':      sumProstoy4,
        'sumProstoy2':      sumProstoy2,

        'avgSpeed':         avgSpeed,
        'avgSpeed4':        avgSpeed4,
        'avgSpeed2':        avgSpeed2,

        'boomOut':          boomOut,

        'allProd':          allProd,
        'allProd4':         allProd4,
        'allProd2':         allProd2,


    })







# блок аунтефикации
@login_required
def profile_view(request):
    return render(request, 'registration/profile.html')
def profileOut_view(request):
    logout(request)
    if request.method == 'GET':
        user_ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if user_ip:
            ip = user_ip.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
    ipMask = ip.split('.')
    if ipMask[2] == "97":
        return redirect('temruk')
    else:
        return redirect('titorovka')


