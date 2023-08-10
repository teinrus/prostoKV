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
def update26(request):
    if request.method == 'POST':

        pk = request.POST.get('pk')
        name = request.POST.get('name')
        v = request.POST.get('value')

        if name == 'uchastok':
            try:
                a = Table26.objects.get(id=pk)
                a.uchastok = v
                a.save()
            except:
                a = Table26(uchastok=v, id=pk)
                a.save()
        elif name == 'prichina':
            try:

                a = Table26.objects.get(id=pk)
                a.prichina = v
                a.save()
            except:
                a = Table26(prichina=v, id=pk)
                a.save()
        elif name == 'otv_pod':
            try:
                a = Table26.objects.get(id=pk)
                a.otv_pod = v
                a.save()
            except:
                a = Table26(otv_pod=v, id=pk)
                a.save()
        elif name == 'comment':
            try:
                a = Table26.objects.get(id=pk)
                a.comment = v
                a.save()
            except:
                a = Table26(comment=v, id=pk)
                a.save()

    return HttpResponse('yes')


# получение данных в таблицу
def update_items26(request):
    if start1 <= datetime.datetime.now().time() <= start2:
        startSmena = datetime.time(8, 00, 0)
        spotSmena = datetime.time(16, 00, 0)
    elif start2 <= datetime.datetime.now().time() <= start3:
        startSmena = datetime.time(16, 00, 0)
        spotSmena = datetime.time(23, 59, 0)
    else:
        startSmena = datetime.time(00, 00, 00)
        spotSmena = datetime.time(8, 00, 00)

    table26 = Table26.objects.filter(startdata=datetime.date.today(),
                                   starttime__gte=startSmena,
                                   starttime__lte=spotSmena)
    print("tut26")
    return render(request, 'Line26/table_body26.html', {'table26': table26})


# получение данных для графика и ячеек
def getData26(requst):
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
                                         GIUDLine='75709045-11b7-11e6-b0ff-005056ac2c77',
                                         ShiftNumber=Smena)
        plan=plan.aggregate(Sum('Quantity')).get('Quantity__sum')
        if plan== None:
            plan=31000
    except:
        plan=31000


    table26 = Table26.objects.filter(startdata=datetime.date.today(),
                                   starttime__gte=startSmena,
                                   starttime__lte=spotSmena)

    speed26 = Speed26.objects.filter(data=datetime.date.today(),
                                   time__gte=startSmena,
                                   time__lte=spotSmena)
    productionOutput26 = ProductionOutput26.objects.filter(data=datetime.date.today(),
                                                         time__gte=startSmena,
                                                         time__lte=spotSmena)



    try:
        count26 = 0
        avg = 0
        for el in speed26:
            if el.triblok != 0:
                count26 += 1
                avg += el.triblok

        avgSpeed26 = round(avg / count26, 2)
    except:
        avgSpeed26 = 0
    try:
        sumProstoy = table26.aggregate(Sum('prostoy')).get('prostoy__sum')

        if (sumProstoy == None):
            sumProstoy = '00:00'
    except:
        sumProstoy = '00:00'
    try:
        sumProduct26 = productionOutput26.aggregate(Sum('production')).get('production__sum')
        if (sumProduct26 == None):
            sumProduct26= '0'
    except:
        sumProduct26 = 0
    try:
        allProc26 = proc(startSmena, spotSmena, plan, sumProduct26)
    except:
        allProc26 = 0

    lableChart26 = []
    dataChart26_triblok = []
    dataChart26_kapsula = []
    dataChart26_eticetka = []
    dataChart26_ukladchik = []
    dataChart26_zakleichik = []

    for sp in speed26:
        lableChart26.append(str(sp.time))
        dataChart26_triblok.append(sp.triblok)
        dataChart26_kapsula.append(sp.kapsula)
        dataChart26_eticetka.append(sp.eticetka)
        dataChart26_ukladchik.append(sp.ukladchik)
        dataChart26_zakleichik.append(sp.zakleichik)

    result = {
        "allProc26": allProc26,
        'sumProstoy26': str(sumProstoy),
        'avgSpeed26': avgSpeed26,
        'sumProduct26': sumProduct26,

        'lableChart26': lableChart26,
        'dataChart26_triblok': dataChart26_triblok,
        'dataChart26_kapsula': dataChart26_kapsula,
        'dataChart26_eticetka': dataChart26_eticetka,
        'dataChart26_ukladchik': dataChart26_ukladchik,
        'dataChart26_zakleichik': dataChart26_zakleichik,

    }
    return JsonResponse(result)

def getBtn26(requst):
    buttons_reg = modbus_client.read_input_registers(2)
    result = {
        'buttons_reg':buttons_reg
              }
    return JsonResponse(result)
