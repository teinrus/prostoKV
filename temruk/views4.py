import datetime


from django.db.models import Count, Sum, Avg
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from temruk.models import *
from  pyModbusTCP.client import ModbusClient
slave_address='192.168.88.230'
port = 502
unit_id = 1
modbus_client = ModbusClient(host=slave_address, port=port,unit_id=unit_id,auto_open=True)

start1 = datetime.time(8, 00, 0)
start2 = datetime.time(20, 00, 0)
start3 = datetime.time(23, 59, 0)





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
def update4(request):
    if request.method == 'POST':

        pk = request.POST.get('pk')
        name = request.POST.get('name')
        v = request.POST.get('value')

        if name == 'uchastok':
            try:
                a = Table4.objects.get(id=pk)
                a.uchastok = v
                a.save()
            except:
                a = Table4(uchastok=v, id=pk)
                a.save()
        elif name == 'prichina':
            try:

                a = Table4.objects.get(id=pk)
                a.prichina = v
                a.save()
            except:
                a = Table4(prichina=v, id=pk)
                a.save()
        elif name == 'otv_pod':
            try:
                a = Table4.objects.get(id=pk)
                a.otv_pod = v
                a.save()
            except:
                a = Table4(otv_pod=v, id=pk)
                a.save()
        elif name == 'comment':
            try:
                a = Table4.objects.get(id=pk)
                a.comment = v
                a.save()
            except:
                a = Table4(comment=v, id=pk)
                a.save()

    return HttpResponse('yes')


# получение данных в таблицу
def update_items4(request):
    if start1 <= datetime.datetime.now().time() < start2:
        startSmena = datetime.time(8, 00, 0)
        spotSmena = datetime.time(20, 00, 0)
        table4 = Table4.objects.filter(startdata=datetime.date.today(),
                                       starttime__gte=startSmena,
                                       starttime__lte=spotSmena)
    elif start2 <= datetime.datetime.now().time():
        startSmena = datetime.time(20, 00, 0)
        spotSmena = datetime.time(23, 59, 0)
        table4 = Table4.objects.filter(startdata=datetime.date.today(),
                                       starttime__gte=startSmena,
                                       starttime__lte=spotSmena)


    elif datetime.datetime.now().time() > start1:
        table4_1 = Table4.objects.filter(startdata=datetime.date.today()-1,
                                       starttime__gte=datetime.time(20, 00, 0),
                                       starttime__lte=datetime.time(23, 59, 0))
        table4_2 = Table4.objects.filter(startdata=datetime.date.today(),
                                       starttime__gte=datetime.time(00, 00, 0),
                                       starttime__lte=datetime.time(8, 00, 0))
        table4=table4_1+table4_2



    list = []
    for table in table4:
        table_info = {
            'id': table.id,
            'startdata': table.startdata,
            'starttime': table.starttime,
            'prostoy': table.prostoy,

            'uchastok': table.uchastok,
            'otv_pod': table.otv_pod,
            'prichina': table.prichina,
            'comment': table.comment,
        }
        list.append(table_info)

    table_dic = {}
    table_dic['data'] = list

    return render(request, 'Line4/table_body4.html', {'table4': table4})


# получение данных для графика и ячеек
def getData4(requst):

    if start1 <= datetime.datetime.now().time() < start2:
        startSmena = datetime.time(8, 00, 0)
        spotSmena = datetime.time(20, 00, 0)
        table4 = Table4.objects.filter(startdata=datetime.date.today(),
                                       starttime__gte=startSmena,
                                       starttime__lte=spotSmena)
        speed4 = Speed4.objects.filter(data=datetime.date.today(),
                                       time__gte=startSmena,
                                       time__lte=spotSmena)
        productionOutput4 = ProductionOutput4.objects.filter(data=datetime.date.today(),
                                                             time__gte=startSmena,
                                                             time__lte=spotSmena)
        Smena=1
    elif start2 <= datetime.datetime.now().time():
        startSmena = datetime.time(20, 00, 0)
        spotSmena = datetime.time(23, 59, 0)
        table4 = Table4.objects.filter(startdata=datetime.date.today(),
                                       starttime__gte=startSmena,
                                       starttime__lte=spotSmena)
        table4 = Table4.objects.filter(startdata=datetime.date.today(),
                                       starttime__gte=startSmena,
                                       starttime__lte=spotSmena)
        speed4 = Speed4.objects.filter(data=datetime.date.today(),
                                       time__gte=startSmena,
                                       time__lte=spotSmena)
        productionOutput4 = ProductionOutput4.objects.filter(data=datetime.date.today(),
                                                             time__gte=startSmena,
                                                             time__lte=spotSmena)

        Smena = 2
    elif datetime.datetime.now().time() < start1:

        Smena = 2
        print(Smena)
        table4_1 = Table4.objects.filter(startdata=datetime.date.today()-datetime.timedelta(days=1),
                                       starttime__gte=datetime.time(20, 00, 0),
                                       starttime__lte=datetime.time(23, 59, 0))
        table4_2 = Table4.objects.filter(startdata=datetime.date.today(),
                                       starttime__gte=datetime.time(00, 00, 0),
                                       starttime__lte=datetime.time(8, 00, 0))
        table4=table4_1|table4_2
        speed4_1 = Speed4.objects.filter(startdata=datetime.date.today() - datetime.timedelta(days=1),
                                         starttime__gte=datetime.time(20, 00, 0),
                                         starttime__lte=datetime.time(23, 59, 0))
        speed4_2 = Speed4.objects.filter(startdata=datetime.date.today(),
                                         starttime__gte=datetime.time(00, 00, 0),
                                         starttime__lte=datetime.time(8, 00, 0))
        speed4 = speed4_1|speed4_2
        productionOutput4_1 = ProductionOutput4.objects.filter(startdata=datetime.date.today() - datetime.timedelta(days=1),
                                         starttime__gte=datetime.time(20, 00, 0),
                                         starttime__lte=datetime.time(23, 59, 0))
        productionOutput4_2 = ProductionOutput4.objects.filter(startdata=datetime.date.today(),
                                         starttime__gte=datetime.time(00, 00, 0),
                                         starttime__lte=datetime.time(8, 00, 0))
        productionOutput4 = productionOutput4_1|productionOutput4_2

    try:
        plan = bottling_plan.objects.filter(Data=datetime.date.today(),
                                         GIUDLine='b84d1e71-1109-11e6-b0ff-005056ac2c77',
                                         ShiftNumber=Smena)
        plan=plan.aggregate(Sum('Quantity')).get('Quantity__sum')
        if plan== None:
            plan=31000

    except:
        plan=31000





    try:
        count4 = 0
        avg = 0
        for el in speed4:
            if el.triblok != 0:
                count4 += 1
                avg += el.triblok

        avgSpeed = round(avg / count4, 2)
    except:
        avgSpeed = 0
    try:
        sumProstoy = table4.aggregate(Sum('prostoy')).get('prostoy__sum')

        if (sumProstoy == None):
            sumProstoy = '00:00'
    except:
        sumProstoy = '00:00'
    try:
        sumProduct4 = productionOutput4.aggregate(Sum('production')).get('production__sum')
        if (sumProduct4 == None):
            sumProduct4 = '0'
    except:
        sumProduct4 = 0
    try:
        allProc4 = proc(startSmena, spotSmena, plan, sumProduct4)
    except:
        allProc4 = 0

    lableChart4 = []
    dataChart4_triblok = []
    dataChart4_kapsula = []
    dataChart4_eticetka = []
    dataChart4_ukladchik = []
    dataChart4_zakleichik = []

    for sp in speed4:
        lableChart4.append(str(sp.time))
        dataChart4_triblok.append(sp.triblok)
        dataChart4_kapsula.append(sp.kapsula)
        dataChart4_eticetka.append(sp.eticetka)
        dataChart4_ukladchik.append(sp.ukladchik)
        dataChart4_zakleichik.append(sp.zakleichik)

    result = {
        "allProc4": allProc4,
        'sumProstoy4': str(sumProstoy),
        'avgSpeed4': avgSpeed,
        'sumProduct4': sumProduct4,

        'lableChart4': lableChart4,
        'dataChart4_triblok': dataChart4_triblok,
        'dataChart4_kapsula': dataChart4_kapsula,
        'dataChart4_eticetka': dataChart4_eticetka,
        'dataChart4_ukladchik': dataChart4_ukladchik,
        'dataChart4_zakleichik': dataChart4_zakleichik,

    }
    return JsonResponse(result)
def getBtn4(requst):
    buttons_reg = modbus_client.read_input_registers(1)
    result = {
        'buttons_reg':buttons_reg
              }
    return JsonResponse(result)
