import datetime


from django.db.models import Count, Sum, Avg
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from temruk.models import bottling_plan, prichina, uchastok
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
def update25(request):
    if request.method == 'POST':
        pk = request.POST.get('pk')
        name = request.POST.get('name')
        value = request.POST.get('value')
        if name == "prichina":
            b = Table25.objects.get(id=pk).uchastok

            v = uchastok.objects.get(Guid_Line="33b39bdb-a94a-4baf-bf9c-31ab906efb9e",
                                     Uchastok=b).Guid_Uchastok

            try:
                n = "Guid_Uchastok"

                a = Table25.objects.get(id=pk)
                setattr(a, n, v)

            except Table25.DoesNotExist:

                setattr(a, n, v)
            a.save()
            # Запись гуид прицины
            n = "Guid_Prichina"
            v = prichina.objects.get(Prichina=value).Guid_Prichina
            try:
                a = Table25.objects.get(id=pk)
                setattr(a, n, v)

            except Table25.DoesNotExist:
                a = Table25(id=pk, **{n: v})
            a.save()
        if name == "comment" and not Table25.objects.get(id=pk).prichina:
            return HttpResponse('no')

        try:
            a = Table25.objects.get(id=pk)
            setattr(a, name, value)
        except Table25.DoesNotExist:
            a = Table25(id=pk, **{name: value})

        a.save()
        return HttpResponse('yes')


# получение данных в таблицу
def update_items25(request):
    if start1 <= datetime.datetime.now().time() <= start2:
        startSmena = datetime.time(8, 00, 0)
        spotSmena = datetime.time(16, 00, 0)
    elif start2 <= datetime.datetime.now().time() <= start3:
        startSmena = datetime.time(16, 00, 0)
        spotSmena = datetime.time(23, 59, 0)
    else:
        startSmena = datetime.time(00, 00, 00)
        spotSmena = datetime.time(8, 00, 00)

    table25 = Table25.objects.filter(startdata=datetime.date.today(),
                                   starttime__gte=startSmena,
                                   starttime__lte=spotSmena)

    return render(request, 'Line25/table_body25.html', {'table25': table25})


# получение данных для графика и ячеек
def getData25(requst):
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
                                         GIUDLine='33b39bdb-a94a-4baf-bf9c-31ab906efb9e',
                                         ShiftNumber=Smena)
        plan=plan.aggregate(Sum('Quantity')).get('Quantity__sum')
        if plan== None:
            plan=31000
    except:
        plan=31000


    table25 = Table25.objects.filter(startdata=datetime.date.today(),
                                   starttime__gte=startSmena,
                                   starttime__lte=spotSmena)

    speed25 = Speed25.objects.filter(data=datetime.date.today(),
                                   time__gte=startSmena,
                                   time__lte=spotSmena)
    productionOutput25 = ProductionOutput25.objects.filter(data=datetime.date.today(),
                                                         time__gte=startSmena,
                                                         time__lte=spotSmena)



    try:
        count25 = 0
        avg = 0
        for el in speed25:
            if el.triblok != 0:
                count25 += 1
                avg += el.triblok

        avgSpeed25 = round(avg / count25, 2)
    except:
        avgSpeed25 = 0
    try:
        sumProstoy = table25.aggregate(Sum('prostoy')).get('prostoy__sum')

        if (sumProstoy == None):
            sumProstoy = '00:00'
    except:
        sumProstoy = '00:00'
    try:
        sumProduct25 = productionOutput25.aggregate(Sum('production')).get('production__sum')
        if (sumProduct25 == None):
            sumProduct25= '0'
    except:
        sumProduct25 = 0
    try:
        allProc25 = proc(startSmena, spotSmena, plan, sumProduct25)
    except:
        allProc25 = 0

    lableChart25 = []
    dataChart25_triblok = []
    dataChart25_kapsula = []
    dataChart25_eticetka = []
    dataChart25_ukladchik = []
    dataChart25_zakleichik = []

    for sp in speed25:
        lableChart25.append(str(sp.time))
        dataChart25_triblok.append(sp.triblok)
        dataChart25_kapsula.append(sp.kapsula)
        dataChart25_eticetka.append(sp.eticetka)
        dataChart25_ukladchik.append(sp.ukladchik)
        dataChart25_zakleichik.append(sp.zakleichik)

    result = {
        "allProc25": allProc25,
        'sumProstoy25': str(sumProstoy),
        'avgSpeed25': avgSpeed25,
        'sumProduct25': sumProduct25,

        'lableChart25': lableChart25,
        'dataChart25_triblok': dataChart25_triblok,
        'dataChart25_kapsula': dataChart25_kapsula,
        'dataChart25_eticetka': dataChart25_eticetka,
        'dataChart25_ukladchik': dataChart25_ukladchik,
        'dataChart25_zakleichik': dataChart25_zakleichik,

    }
    return JsonResponse(result)

def getBtn25(requst):
    buttons_reg = modbus_client.read_input_registers(1)
    result = {
        'buttons_reg':buttons_reg
              }
    return JsonResponse(result)
