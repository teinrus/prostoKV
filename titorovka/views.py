from django.http import HttpResponse
from django.shortcuts import render
from .forms import Otchet

# Create your views here.
from titorovka.models import titorovka


def index (request):
    return render(request, "titorovka.html", {

    })

def Sotchet (request):
    form = Otchet(request.GET)

    return render(request, "Sotchet.html", {
        'form': form,

    })
