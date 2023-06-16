import datetime

from django.db.models import  Sum, Avg
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from temruk.models import *

from  pyModbusTCP.client import ModbusClient
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

# получение данных в таблицу
def update_items5(request):
    if start1 <= datetime.datetime.now().time() <= start2:
        startSmena = datetime.time(8, 00, 0)
        spotSmena = datetime.time(16, 30, 0)
    elif start2 <= datetime.datetime.now().time() <= start3:
        startSmena = datetime.time(16, 30, 0)
        spotSmena = datetime.time(23, 59, 0)
    else:
        startSmena = datetime.time(00, 00, 00)
        spotSmena = datetime.time(8, 00, 00)

    table5 = Table5.objects.filter(startdata=datetime.date.today(),
                                   starttime__gte=startSmena,
                                   starttime__lte=spotSmena)
    list = []
    for table in table5:
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

    return render(request, 'Line5/table_body.html', {'table5': table5})



# получение данных для 4 блоков и графика
def getData(requst):


    if start1 < datetime.datetime.now().time() <= start2:
        startSmena = datetime.time(8, 00, 0)
        spotSmena = datetime.time(16, 30, 0)
        Smena=1
    elif start2 <= datetime.datetime.now().time() <= start3:
        startSmena = datetime.time(16, 30, 0)
        spotSmena = datetime.time(23, 59, 0)
        Smena=2
    else:
        startSmena = datetime.time(00, 00, 00)
        spotSmena = datetime.time(8, 00, 00)
        Smena=3

    table = Table5.objects.filter(startdata=datetime.date.today(),
                                  starttime__gte=startSmena,
                                  starttime__lte=spotSmena)
    speed = Speed5.objects.filter(data=datetime.date.today(),
                                  time__gte=startSmena,
                                  time__lte=spotSmena)

    boom = bottleExplosion5.objects.filter(data=datetime.date.today(),
                                          time__gte=startSmena,
                                          time__lte=spotSmena)
    productionOutput5 = ProductionOutput5.objects.filter(data=datetime.date.today(),
                                  time__gte=startSmena,
                                  time__lte=spotSmena)
    try:
        plan = bottling_plan.objects.filter(Data=datetime.date.today(),
                                         GIUDLine='22b8afd6-110a-11e6-b0ff-005056ac2c77',
                                         ShiftNumber=Smena)
        plan=plan.aggregate(Sum('Quantity')).get('Quantity__sum')
        if plan== None:
            plan=31000
    except:
        plan=31000

    try:
        count5=0
        avg=0
        for el in speed:
            if el.triblok!=0:
                count5+=1
                avg+=el.triblok

        avgSpeed = round(avg/count5, 2)
    except:
        avgSpeed = 0
    try:
        sumProstoy = table.aggregate(Sum('prostoy')).get('prostoy__sum')

        if (sumProstoy == None):
            sumProstoy = '00:00'
    except:
        sumProstoy = '00:00'
    try:
        sum=0
        sumProduct = productionOutput5.aggregate(Sum('production')).get('production__sum')
        for el in productionOutput5:
            sum+=el.production
    except:
        sumProduct = 0
    try:

        allProc = proc(startSmena, spotSmena, plan, sumProduct),
    except:

        allProc = 0

    try:
        boomOut = boom.aggregate(Sum('bottle')).get('bottle__sum')
        if (boomOut == None):
            boomOut = 0
    except:
        boomOut = 0

    lableChart = []
    dataChart_triblok = []
    dataChart_muzle = []
    dataChart_termotunel = []
    dataChart4_kapsula = []
    dataChart4_eticetka = []
    dataChart4_ukladchik = []
    dataChart4_zakleichik = []

    for sp in speed:
        lableChart.append(str(sp.time))
        dataChart_triblok.append(sp.triblok)
        dataChart_muzle.append(sp.muzle)
        dataChart_termotunel.append(sp.termotunel)
        dataChart4_kapsula.append(sp.kapsula)
        dataChart4_eticetka.append(sp.eticetka)
        dataChart4_ukladchik.append(sp.ukladchik)
        dataChart4_zakleichik.append(sp.zakleichik)


    result = {"allProc": allProc,
              "boomOut": boomOut,
              'sumProstoy': str(sumProstoy),
              'sumProduct': sumProduct,
              'avgSpeed': avgSpeed,

              'lableChart': lableChart,

              'dataChart_triblok': dataChart_triblok,
              'dataChart_muzle':dataChart_muzle,
              'dataChart_termotunel' :dataChart_termotunel,
              'dataChart4_kapsula' :dataChart4_kapsula,
              'dataChart4_eticetka':dataChart4_eticetka,
              'dataChart4_ukladchik':dataChart4_ukladchik,
              'dataChart4_zakleichik':dataChart4_zakleichik,


              }
    return JsonResponse(result)



# блок внесения изменения в таблицу
def update(request):
    if request.method == 'POST':

        pk = request.POST.get('pk')
        name = request.POST.get('name')
        v = request.POST.get('value')

        if name == 'uchastok':
            try:
                a = Table5.objects.get(id=pk)
                a.uchastok = v
                a.save()
            except:
                a = Table5(uchastok=v, id=pk)
                a.save()
        elif name == 'prichina':
            try:

                a = Table5.objects.get(id=pk)
                a.prichina = v
                a.save()
            except:
                a = Table5(prichina=v, id=pk)
                a.save()
        elif name == 'otv_pod':
            try:
                a = Table5.objects.get(id=pk)
                a.otv_pod = v
                a.save()
            except:
                a = Table5(otv_pod=v, id=pk)
                a.save()
        elif name == 'comment':
            try:
                a = Table5.objects.get(id=pk)
                a.comment = v
                a.save()
            except:
                a = Table5(comment=v, id=pk)
                a.save()

    return HttpResponse('yes')

def getBtn5(requst):
    buttons_reg = modbus_client.read_input_registers(0)
    result = {
        'buttons_reg':buttons_reg
              }
    return JsonResponse(result)