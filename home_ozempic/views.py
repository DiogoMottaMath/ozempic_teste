from django.shortcuts import render, redirect
from .forms import CalculadoraDoseForm
import math
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse


def pagina_inicial(request):
    form = CalculadoraDoseForm()
       
    if request.method == 'POST':
         form = CalculadoraDoseForm(request.POST)
         if form.is_valid():
            peso = form.cleaned_data['peso']
            altura = form.cleaned_data['altura']
            tem_diabetes = form.cleaned_data['tem_diabetes']
            tem_problemas_cardiacos = form.cleaned_data['tem_problemas_cardiacos']
            dose_alvo = form.cleaned_data['dose_alvo']

            imc = peso / ((altura / 100) ** 2)
            
            if tem_problemas_cardiacos or tem_diabetes or imc >= 35:
                nivel_saude = 'sedentario'
            elif imc >= 30:
                nivel_saude = 'levemente_ativo'
            elif imc >= 25:
                nivel_saude = 'moderadamente_ativo'
            else:
                nivel_saude = 'altamente_ativo'

            dose_inicial_sugerida = None
            num_semanas_sugerido = None
            tipo_progressao_sugerido = None

    
            if nivel_saude == 'sedentario':
                dose_inicial_sugerida = 0.5
                num_semanas_sugerido = 16
                tipo_progressao_sugerido = 'pa'
            elif nivel_saude == 'levemente_ativo':
                dose_inicial_sugerida = 0.5
                num_semanas_sugerido = 12
                tipo_progressao_sugerido = 'pa'
            elif nivel_saude == 'moderadamente_ativo':
                dose_inicial_sugerida = 1.0
                num_semanas_sugerido = 9
                tipo_progressao_sugerido = 'pg'
            elif nivel_saude == 'altamente_ativo':
                dose_inicial_sugerida = 1.0
                num_semanas_sugerido = 6
                tipo_progressao_sugerido = 'pg'
            else:
             sugestoes = {'erro': 'Não foi possível determinar o nível de saúde.'}
             dose_inicial_sugerida = 0  # Valores padrão para evitar erros posteriores
             num_semanas_sugerido = 0
             tipo_progressao_sugerido = 'pa' # Ou outro padrão

            cronograma_list = []
            if num_semanas_sugerido > 0:
                if tipo_progressao_sugerido == 'pa':
                    if num_semanas_sugerido > 1:
                        razao = (dose_alvo - dose_inicial_sugerida) / (num_semanas_sugerido - 1)
                    else:
                        razao = 0
                    for semana in range(1, num_semanas_sugerido + 1):
                        dose = dose_inicial_sugerida + (semana - 1) * razao
                        cronograma_list.append(f'Semana {semana}: {dose:.2f} mg')
                elif tipo_progressao_sugerido == 'pg':
                    if dose_inicial_sugerida <= 0 or dose_alvo <= 0:
                        request.session['erro_cronograma'] = 'Dose inicial e alvo devem ser positivas para progressão geométrica.'
                    elif num_semanas_sugerido > 1:
                        razao = (dose_alvo / dose_inicial_sugerida)**(1/(num_semanas_sugerido - 1))
                    else:
                        razao = 1
                    for semana in range(1, num_semanas_sugerido + 1):
                        dose = dose_inicial_sugerida * (razao**(semana - 1))
                        cronograma_list.append(f'Semana {semana}: {dose:.2f} mg')
            else:
                request.session['erro_cronograma'] = 'Número de semanas inválido.'

            request.session['nivel_saude'] = nivel_saude
            request.session['dose_inicial'] = dose_inicial_sugerida
            request.session['num_semanas'] = num_semanas_sugerido
            request.session['tipo_progressao'] = 'Progressão Aritmética' if tipo_progressao_sugerido == 'pa' else 'Progressão Geométrica'
            request.session['cronograma'] = cronograma_list

            return redirect(reverse('exibir_cronograma'))
         else:
            context = {'form': form}
            return render(request, 'pagina_inicial.html', context)
    else:
        context = {'form': form}
        return render(request, 'pagina_inicial.html', context)
    
def exibir_cronograma(request):
    context = {
        'nivel_saude': request.session.get('nivel_saude'),
        'dose_inicial': request.session.get('dose_inicial'),
        'num_semanas': request.session.get('num_semanas'),
        'tipo_progressao': request.session.get('tipo_progressao'),
        'cronograma': request.session.get('cronograma'),
        'erro_sugestoes': request.session.get('erro_sugestoes'),
        'erro_cronograma': request.session.get('erro_cronograma'),
        'form': CalculadoraDoseForm() # Passa o formulário para o link de voltar
    }
    return render(request, 'exibir_cronograma.html', context)

def index(request):
    if request.method == 'GET':
     return render(request, 'index.html')
    
    if request.method == 'POST':
     return redirect('pagina_inicial')
    






   
        
                


    




