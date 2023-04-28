

from django import forms
from django.forms import NumberInput


class Otchet(forms.Form):

    start_data = forms.DateField(widget=NumberInput(attrs={'type':'date'}),required=False,label="Начало")

    finish_data= forms.DateField(required=False,widget=NumberInput(attrs={'type':'date'}),label='Конец')

    Smena = (('Смена 0', 'Все'),('Смена 1', 'Смена 1'), ('Смена 2', 'Смена 2'),('Смена 3', 'Смена 3'),)
    SmenaF = forms.ChoiceField(choices=Smena,required=False,label='Смена')

    Line = (('Линиия 5', 'Линиия 5'), ('Линиия 2', 'Линиия 2'),)
    LineF = forms.ChoiceField(choices=Line, required=False, label='Линиия')
