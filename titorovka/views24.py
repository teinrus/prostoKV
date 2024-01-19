import datetime


from django.db.models import Count, Sum, Avg
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from temruk.models import bottling_plan
from titorovka.models import *
from  pyModbusTCP.client import ModbusClient
slave_address='10.36.20.4'

unit_id = 1
modbus_client = ModbusClient(host=slave_address, unit_id=unit_id,auto_open=True)

start1 = datetime.time(8, 00, 0)
start2 = datetime.time(16, 00, 0)
start3 = datetime.time(23, 59, 0)

if start1 <= datetime.datetime.now().time() <= start2:
    startSmena = datetime.time(8, 00, 0)
    spotSmena = datetime.time(16, 00, 0)
elif start2 <= datetime.datetime.now().time() <= start3:
    startSmena = datetime.time(16, 00, 0)
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

    planProdSec = (plan / diff1.total_seconds())
    # количество времени которое прошло
    d_start2 = datetime.datetime.combine(today, startSmena)
    d_end2 = datetime.datetime.combine(today, datetime.datetime.now().time())
    diff2 = d_end2 - d_start2

    # проц вып продукции
    return int(colProduct / ((int(diff2.total_seconds()) * planProdSec) / 100))


# изменение в таблице
def update24(request):
    if request.method == 'POST':

        pk = request.POST.get('pk')
        name = request.POST.get('name')
        value = request.POST.get('value')
        if name == "comment" and not Table24.objects.get(id=pk).prichina:
            return HttpResponse('no')

        try:
            a = Table24.objects.get(id=pk)
            setattr(a, name, value)
        except Table24.DoesNotExist:
            a = Table24(id=pk, **{name: value})

        a.save()
        return HttpResponse('yes')

    return HttpResponse('yes')


# получение данных в таблицу
def update_items24(request):
    if start1 <= datetime.datetime.now().time() <= start2:
        startSmena = datetime.time(8, 00, 0)
        spotSmena = datetime.time(16, 00, 0)
    elif start2 <= datetime.datetime.now().time() <= start3:
        startSmena = datetime.time(16, 00, 0)
        spotSmena = datetime.time(23, 59, 0)
    else:
        startSmena = datetime.time(00, 00, 00)
        spotSmena = datetime.time(8, 00, 00)

    table24 = Table24.objects.filter(startdata=datetime.date.today(),
                                   starttime__gte=startSmena,
                                   starttime__lte=spotSmena)

    return render(request, 'Line24/table_body24.html', {'table24': table24})


# получение данных для графика и ячеек
def getData24(requst):
    if start1 <= datetime.datetime.now().time() <= start2:
        startSmena = datetime.time(8, 00, 0)
        spotSmena = datetime.time(16, 00, 0)
        Smena = 1
    elif start2 <= datetime.datetime.now().time() <= start3:
        startSmena = datetime.time(16, 00, 0)
        spotSmena = datetime.time(23, 59, 0)
        Smena = 2
    else:
        startSmena = datetime.time(00, 00, 00)
        spotSmena = datetime.time(8, 00, 00)
        Smena = 3

    try:
        plan = bottling_plan.objects.filter(Data=datetime.date.today(),
                                         GIUDLine='90aef8a3-8edd-4904-b22b-8f53d903f90d',
                                         ShiftNumber=Smena)
        plan=plan.aggregate(Sum('Quantity')).get('Quantity__sum')
        if plan== None:
            plan=31000
    except:
        plan=31000


    table24 = Table24.objects.filter(startdata=datetime.date.today(),
                                   starttime__gte=startSmena,
                                   starttime__lte=spotSmena)

    speed24 = Speed24.objects.filter(data=datetime.date.today(),
                                   time__gte=startSmena,
                                   time__lte=spotSmena)
    productionOutput24 = ProductionOutput24.objects.filter(data=datetime.date.today(),
                                                         time__gte=startSmena,
                                                         time__lte=spotSmena)



    try:
        count24 = 0
        avg = 0
        for el in speed24:
            if el.triblok != 0:
                count24 += 1
                avg += el.triblok

        avgSpeed24 = round(avg / count24, 2)
    except:
        avgSpeed24 = 0
    try:
        sumProstoy = table24.aggregate(Sum('prostoy')).get('prostoy__sum')

        if (sumProstoy == None):
            sumProstoy = '00:00'
    except:
        sumProstoy = '00:00'
    try:
        sumProduct24 = productionOutput24.aggregate(Sum('production')).get('production__sum')
        if (sumProduct24 == None):
            sumProduct24= '0'
    except:
        sumProduct24 = 0
    try:
        allProc24 = proc(startSmena, spotSmena, plan, sumProduct24)
    except:
        allProc24 = 0

    lableChart24 = []
    dataChart24_triblok = []
    dataChart24_kapsula = []
    dataChart24_eticetka = []
    dataChart24_ukladchik = []
    dataChart24_zakleichik = []

    for sp in speed24:
        lableChart24.append(str(sp.time))
        dataChart24_triblok.append(sp.triblok)
        dataChart24_kapsula.append(sp.kapsula)
        dataChart24_eticetka.append(sp.eticetka)
        dataChart24_ukladchik.append(sp.ukladchik)
        dataChart24_zakleichik.append(sp.zakleichik)

    result = {
        "allProc24": allProc24,
        'sumProstoy24': str(sumProstoy),
        'avgSpeed24': avgSpeed24,
        'sumProduct24': sumProduct24,

        'lableChart24': lableChart24,
        'dataChart24_triblok': dataChart24_triblok,
        'dataChart24_kapsula': dataChart24_kapsula,
        'dataChart24_eticetka': dataChart24_eticetka,
        'dataChart24_ukladchik': dataChart24_ukladchik,
        'dataChart24_zakleichik': dataChart24_zakleichik,

    }
    return JsonResponse(result)

def getBtn24(requst):
    buttons_reg = modbus_client.read_input_registers(0)
    result = {
        'buttons_reg':buttons_reg
              }
    return JsonResponse(result)
