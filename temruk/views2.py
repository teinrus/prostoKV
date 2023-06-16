import datetime
from  pyModbusTCP.client import ModbusClient


from django.db.models import Count, Sum, Avg
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from temruk.models import *

slave_address='192.168.88.230'
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

#изменение в таблице
def update2(request):
    if request.method == 'POST':

        pk = request.POST.get('pk')
        name = request.POST.get('name')
        v = request.POST.get('value')

        if name == 'uchastok':
            try:
                a = Table2.objects.get(id=pk)
                a.uchastok = v
                a.save()
            except:
                a = Table2(uchastok=v, id=pk)
                a.save()
        elif name == 'prichina':
            try:

                a = Table2.objects.get(id=pk)
                a.prichina = v
                a.save()
            except:
                a = Table2(prichina=v, id=pk)
                a.save()
        elif name == 'otv_pod':
            try:
                a = Table2.objects.get(id=pk)
                a.otv_pod = v
                a.save()
            except:
                a = Table2(otv_pod=v, id=pk)
                a.save()
        elif name == 'comment':
            try:
                a = Table2.objects.get(id=pk)
                a.comment = v
                a.save()
            except:
                a = Table2(comment=v, id=pk)
                a.save()

    return HttpResponse('yes')

# получение данных в таблицу
def update_items2(request):
    if start1 <= datetime.datetime.now().time() <= start2:
        startSmena = datetime.time(8, 00, 0)
        spotSmena = datetime.time(16, 30, 0)
    elif start2 <= datetime.datetime.now().time() <= start3:
        startSmena = datetime.time(16, 30, 0)
        spotSmena = datetime.time(23, 59, 0)
    else:
        startSmena = datetime.time(00, 00, 00)
        spotSmena = datetime.time(8, 00, 00)

    table2 = Table2.objects.filter(startdata=datetime.date.today(),
                                   starttime__gte=startSmena,
                                   starttime__lte=spotSmena)



    return render(request, 'Line2/table_body2.html', {'table2': table2})

# получение данных для графика и ячеек
def getData2(requst):

    if start1 <= datetime.datetime.now().time() <= start2:
        startSmena = datetime.time(8, 00, 0)
        spotSmena = datetime.time(16, 30, 0)
        Smena=1
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
                                         GIUDLine='48f7e8d8-1114-11e6-b0ff-005056ac2c77',
                                         ShiftNumber=Smena)
        plan=plan.aggregate(Sum('Quantity')).get('Quantity__sum')
        if plan== None:
            plan=31000
        print(plan)
    except:
        plan=31000


    table2 = Table2.objects.filter(startdata=datetime.date.today(),
                                  starttime__gte=startSmena,
                                  starttime__lte=spotSmena)
    speed2 = Speed2.objects.filter(data=datetime.date.today(),
                                  time__gte=startSmena,
                                  time__lte=spotSmena)
    productionOutput2=ProductionOutput2.objects.filter(data=datetime.date.today(),
                                  time__gte=startSmena,
                                  time__lte=spotSmena)

    try:
        count2=0
        avg=0
        for el in speed2:
            if el.triblok!=0:
                count2+=1
                avg+=el.triblok

        avgSpeed = round(avg/count2, 2)
    except:
        avgSpeed = 0
    try:
        sumProstoy = table2.aggregate(Sum('prostoy')).get('prostoy__sum')

        if (sumProstoy == None):
            sumProstoy = '00:00'
    except:
        sumProstoy = '00:00'
    try:
        sumProduct2 = productionOutput2.aggregate(Sum('production')).get('production__sum')
        if sumProduct2 == None:
            sumProduct2=0
    except:
        sumProduct2 = 0
    try:
        allProc2 = proc(startSmena, spotSmena, plan, sumProduct2)

    except:
        allProc2 = 0






    lableChart2 = []
    dataChart2 = []

    for sp in speed2:
        lableChart2.append(str(sp.time))
        dataChart2.append(sp.triblok)



    result = {

            "allProc2": allProc2,
            'sumProstoy2': str(sumProstoy),
            'avgSpeed2': avgSpeed,
            'sumProduct2':sumProduct2,

            'lableChart2': lableChart2,
            'dataChart2': dataChart2,


              }
    return JsonResponse(result)
def getBtn2(requst):
    buttons_reg = modbus_client.read_input_registers(2)

    result = {
        'buttons_reg':buttons_reg
              }

    return JsonResponse(result)



