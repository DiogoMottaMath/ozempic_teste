from django import forms

class CalculadoraDoseForm(forms.Form):
    peso = forms.FloatField(label='Peso (kg)')
    altura = forms.FloatField(label='Altura (cm)')
    tem_diabetes = forms.BooleanField(label='Tem Diabetes?', required=False)
    tem_problemas_cardiacos = forms.BooleanField(label='Tem Problemas Cardíacos?', required=False)
    dose_alvo = forms.FloatField(label='Dose Alvo Sugerida pelo Médico (mg)')
    