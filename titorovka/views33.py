import datetime


from django.db.models import Count, Sum, Avg
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from temruk.models import bottling_plan
from titorovka.models import *
from  pyModbusTCP.client import ModbusClient
slave_address='192.168.94.114'
port = 502
unit_id = 1
modbus_client = ModbusClient(host=slave_address, port=port,unit_id=unit_id,auto_open=True)

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

    planProdSec = (plan / diff1.total_seconds())
    # количество времени которое прошло
    d_start2 = datetime.datetime.combine(today, startSmena)
    d_end2 = datetime.datetime.combine(today, datetime.datetime.now().time())
    diff2 = d_end2 - d_start2

    # проц вып продукции
    return int(colProduct / ((int(diff2.total_seconds()) * planProdSec) / 100))


# изменение в таблице
def update33(request):
    if request.method == 'POST':

        pk = request.POST.get('pk')
        name = request.POST.get('name')
        v = request.POST.get('value')

        if name == 'uchastok':
            try:
                a = Table33.objects.get(id=pk)
                a.uchastok = v
                a.save()
            except:
                a = Table33(uchastok=v, id=pk)
                a.save()
        elif name == 'prichina':
            try:

                a = Table33.objects.get(id=pk)
                a.prichina = v
                a.save()
            except:
                a = Table33(prichina=v, id=pk)
                a.save()
        elif name == 'otv_pod':
            try:
                a = Table33.objects.get(id=pk)
                a.otv_pod = v
                a.save()
            except:
                a = Table33(otv_pod=v, id=pk)
                a.save()
        elif name == 'comment':
            try:
                a = Table33.objects.get(id=pk)
                a.comment = v
                a.save()
            except:
                a = Table33(comment=v, id=pk)
                a.save()

    return HttpResponse('yes')


# получение данных в таблицу
def update_items33(request):
    if start1 <= datetime.datetime.now().time() <= start2:
        startSmena = datetime.time(8, 00, 0)
        spotSmena = datetime.time(16, 30, 0)
    elif start2 <= datetime.datetime.now().time() <= start3:
        startSmena = datetime.time(16, 30, 0)
        spotSmena = datetime.time(23, 59, 0)
    else:
        startSmena = datetime.time(00, 00, 00)
        spotSmena = datetime.time(8, 00, 00)

    table33 = Table33.objects.filter(startdata=datetime.date.today(),
                                   starttime__gte=startSmena,
                                   starttime__lte=spotSmena)

    return render(request, 'Line33/table_body33.html', {'table33': table33})


# получение данных для графика и ячеек
def getData33(requst):
    if start1 <= datetime.datetime.now().time() <= start2:
        startSmena = datetime.time(8, 00, 0)
        spotSmena = datetime.time(16, 30, 0)
        Smena = 1
    elif start2 <= datetime.datetime.now().time() <= start3:
        startSmena = datetime.time(16, 30, 0)
        spotSmena = datetime.time(23, 59, 0)
        Smena = 2
    else:
        startSmena = datetime.time(00, 00, 00)
        spotSmena = datetime.time(8, 00, 00)
        Smena = 3

    try:
        plan = bottling_plan.objects.filter(Data=datetime.date.today(),
                                         GIUDLine='d65654f8-2e89-4044-bb10-4342a9d1b722',
                                         ShiftNumber=Smena)
        plan=plan.aggregate(Sum('Quantity')).get('Quantity__sum')
        if plan== None:
            plan=31000
    except:
        plan=31000


    table33 = Table33.objects.filter(startdata=datetime.date.today(),
                                   starttime__gte=startSmena,
                                   starttime__lte=spotSmena)

    speed33 = Speed33.objects.filter(data=datetime.date.today(),
                                   time__gte=startSmena,
                                   time__lte=spotSmena)
    productionOutput33 = ProductionOutput33.objects.filter(data=datetime.date.today(),
                                                         time__gte=startSmena,
                                                         time__lte=spotSmena)



    try:
        count33 = 0
        avg = 0
        for el in speed33:
            if el.triblok != 0:
                count33 += 1
                avg += el.triblok

        avgSpeed33 = round(avg / count33, 2)
    except:
        avgSpeed33 = 0
    try:
        sumProstoy = table33.aggregate(Sum('prostoy')).get('prostoy__sum')

        if (sumProstoy == None):
            sumProstoy = '00:00'
    except:
        sumProstoy = '00:00'
    try:
        sumProduct33 = productionOutput33.aggregate(Sum('production')).get('production__sum')
        if (sumProduct33 == None):
            sumProduct33= '0'
    except:
        sumProduct33 = 0
    try:
        allProc33 = proc(startSmena, spotSmena, plan, sumProduct33)
    except:
        allProc33 = 0

    lableChart33 = []
    dataChart33_triblok = []
    dataChart33_kapsula = []
    dataChart33_eticetka = []
    dataChart33_ukladchik = []
    dataChart33_zakleichik = []

    for sp in speed33:
        lableChart33.append(str(sp.time))
        dataChart33_triblok.append(sp.triblok)
        dataChart33_kapsula.append(sp.kapsula)
        dataChart33_eticetka.append(sp.eticetka)
        dataChart33_ukladchik.append(sp.ukladchik)
        dataChart33_zakleichik.append(sp.zakleichik)

    result = {
        "allProc33": allProc33,
        'sumProstoy33': str(sumProstoy),
        'avgSpeed33': avgSpeed33,
        'sumProduct33': sumProduct33,

        'lableChart33': lableChart33,
        'dataChart33_triblok': dataChart33_triblok,
        'dataChart33_kapsula': dataChart33_kapsula,
        'dataChart33_eticetka': dataChart33_eticetka,
        'dataChart33_ukladchik': dataChart33_ukladchik,
        'dataChart33_zakleichik': dataChart33_zakleichik,

    }
    return JsonResponse(result)

def getBtn33(requst):
    buttons_reg = modbus_client.read_input_registers(1)
    result = {
        'buttons_reg':buttons_reg
              }
    return JsonResponse(result)
