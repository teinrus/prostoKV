from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from titorovka.models import titorovka


def homePageView(request):
    test=titorovka.objects.all()
    print(test)
    return HttpResponse('Hello, World!')
