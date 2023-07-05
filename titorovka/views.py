import datetime

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render
from pyModbusTCP.client import ModbusClient

from temruk.models import bottling_plan, prichina, uchastok
from .forms import Otchet

# Create your views here.
from titorovka.models import Table31, ProductionOutput31, Speed31, Table33, Speed33, ProductionOutput33

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

def mod_bus(reg,bit_temp):

    slave_address = '192.168.94.114'
    port = 502
    unit_id = 1
    modbus_client = ModbusClient(host=slave_address, port=port, unit_id=unit_id, auto_open=True)
    test = modbus_client.write_single_register(reg, bit_temp)







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


def index(request):
    if request.method == 'GET':
        table31 = Table31.objects.filter(startdata=datetime.date.today(),
                                      starttime__gte=startSmena,
                                      starttime__lte=spotSmena)
        speed31 = Speed31.objects.filter(data=datetime.date.today(),
                                      time__gte=startSmena,
                                      time__lte=spotSmena)
        table33 = Table33.objects.filter(startdata=datetime.date.today(),
                                      starttime__gte=startSmena,
                                      starttime__lte=spotSmena)
        speed33 = Speed33.objects.filter(data=datetime.date.today(),
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
    return render(request, "titorovka.html", {

        'otv_p':otv_p ,
        'prich': prich,
        'uch': uch,
        'uch_vino': uch_vino,

        'table31': table31,
        'speed31': speed31,
        'table33': table33,
        'speed33': speed33,


    })

def Sotchet(request):

    plan = 0
    table = []
    timeTemp = 0
    form = Otchet(request.GET)
    if form.is_valid():
        # Сортировка по дате
        if form.cleaned_data["start_data"] and form.cleaned_data["finish_data"] and (
                form.cleaned_data["LineF"] == 'Линиия 31'):
            if form.cleaned_data["SmenaF"]:
                if form.cleaned_data["SmenaF"] == 'Смена 0':
                    table = Table31.objects.filter(starttime__gte=datetime.time(0),
                                                  starttime__lte=datetime.time(23, 59),
                                                  startdata__gte=form.cleaned_data["start_data"],
                                                  startdata__lte=form.cleaned_data["finish_data"]
                                                  ).order_by('startdata', 'starttime')

                    speed = Speed31.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(0),
                                                  time__lte=datetime.time(23, 59))

                    prod = ProductionOutput31.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(0),
                                                  time__lte=datetime.time(23, 59))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='12ab36dc-0fb9-44d8-b14d-63230bf1c0cd',
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
                    table = Table31.objects.filter(starttime__gte=datetime.time(8),
                                                  starttime__lte=datetime.time(16, 30),
                                                  startdata__gte=form.cleaned_data["start_data"],
                                                  startdata__lte=form.cleaned_data["finish_data"]
                                                  ).order_by('startdata', 'starttime')
                    speed = Speed31.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(8),
                                                  time__lte=datetime.time(16, 30))

                    prod = ProductionOutput31.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(8),
                                                  time__lte=datetime.time(16, 30))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='12ab36dc-0fb9-44d8-b14d-63230bf1c0cd',
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
                    table = Table31.objects.filter(starttime__gte=datetime.time(16, 30),
                                                  starttime__lte=datetime.time(23, 59),
                                                  startdata__gte=form.cleaned_data["start_data"],
                                                  startdata__lte=form.cleaned_data["finish_data"]
                                                  ).order_by('startdata', 'starttime')
                    speed = Speed31.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(16, 30),
                                                  time__lte=datetime.time(23, 59))

                    prod = ProductionOutput31.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(16, 30),
                                                  time__lte=datetime.time(23, 59))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='12ab36dc-0fb9-44d8-b14d-63230bf1c0cd',
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
                    table = Table31.objects.filter(starttime__gte=datetime.time(00, 00),
                                                  starttime__lte=datetime.time(8, 00),
                                                  startdata__gte=form.cleaned_data["start_data"],
                                                  startdata__lte=form.cleaned_data["finish_data"]
                                                  ).order_by('startdata', 'starttime')
                    speed = Speed31.objects.using('titorovka_db').filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(00, 00),
                                                  time__lte=datetime.time(8, 00))

                    prod = ProductionOutput31.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(00, 00),
                                                  time__lte=datetime.time(8, 00))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='12ab36dc-0fb9-44d8-b14d-63230bf1c0cd',
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
        elif form.cleaned_data["start_data"] and form.cleaned_data["finish_data"] and (
                form.cleaned_data["LineF"] == 'Линиия 33'):
            if form.cleaned_data["SmenaF"]:
                if form.cleaned_data["SmenaF"] == 'Смена 0':
                    table = Table33.objects.filter(starttime__gte=datetime.time(0),
                                                  starttime__lte=datetime.time(23, 59),
                                                  startdata__gte=form.cleaned_data["start_data"],
                                                  startdata__lte=form.cleaned_data["finish_data"]
                                                  ).order_by('startdata', 'starttime')

                    speed = Speed33.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(0),
                                                  time__lte=datetime.time(23, 59))

                    prod = ProductionOutput33.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(0),
                                                  time__lte=datetime.time(23, 59))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='d65654f8-2e89-4044-bb10-4342a9d1b722',
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
                    table = Table33.objects.filter(starttime__gte=datetime.time(8),
                                                  starttime__lte=datetime.time(16, 30),
                                                  startdata__gte=form.cleaned_data["start_data"],
                                                  startdata__lte=form.cleaned_data["finish_data"]
                                                  ).order_by('startdata', 'starttime')
                    speed = Speed33.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(8),
                                                  time__lte=datetime.time(16, 30))

                    prod = ProductionOutput33.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(8),
                                                  time__lte=datetime.time(16, 30))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='d65654f8-2e89-4044-bb10-4342a9d1b722',
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
                    table = Table33.objects.filter(starttime__gte=datetime.time(16, 30),
                                                  starttime__lte=datetime.time(23, 59),
                                                  startdata__gte=form.cleaned_data["start_data"],
                                                  startdata__lte=form.cleaned_data["finish_data"]
                                                  ).order_by('startdata', 'starttime')
                    speed = Speed33.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(16, 30),
                                                  time__lte=datetime.time(23, 59))

                    prod = ProductionOutput33.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(16, 30),
                                                  time__lte=datetime.time(23, 59))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='d65654f8-2e89-4044-bb10-4342a9d1b722',
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
                    table = Table33.objects.filter(starttime__gte=datetime.time(00, 00),
                                                  starttime__lte=datetime.time(8, 00),
                                                  startdata__gte=form.cleaned_data["start_data"],
                                                  startdata__lte=form.cleaned_data["finish_data"]
                                                  ).order_by('startdata', 'starttime')
                    speed = Speed33.objects.using('titorovka_db').filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(00, 00),
                                                  time__lte=datetime.time(8, 00))

                    prod = ProductionOutput33.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(00, 00),
                                                  time__lte=datetime.time(8, 00))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='d65654f8-2e89-4044-bb10-4342a9d1b722',
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



    lableChart = []
    dataChart = []

    #Общее количество  продукции
    try:
        allProd = prod.aggregate(Sum('production')).get('production__sum')
        if (allProd == None):
            allProd = 0
    except:
        allProd = 0



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
    uch_v=uchastok.objects.exclude(uchastok="Мюзлёвочный аппарат")

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



    return render(request, "Sotchet.html", {
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



        'allProd': allProd,

        'lableChart': lableChart,
        'dataChart': dataChart,

        'otv_p': otv_p,
        'prich': prich,
        'uch': uch,
        'uch_v':uch_v,



    })


def start_perenaladka31(request):
    mod_bus(0,1)
    return HttpResponse('yes')
def start_donaladka31(request):
    mod_bus(0,2)
    return HttpResponse('yes')

def rabota31(request):
    mod_bus(0,4)
    return HttpResponse('yes')
def TO31(request):
    mod_bus(0,8)
    return HttpResponse('yes')

def start_perenaladka33(request):
    mod_bus(1,1)
    return HttpResponse('yes')
def start_donaladka33(request):
    mod_bus(1,2)
    return HttpResponse('yes')

def rabota33(request):
    mod_bus(1,4)
    return HttpResponse('yes')
def TO33(request):
    mod_bus(1,8)
    return HttpResponse('yes')




