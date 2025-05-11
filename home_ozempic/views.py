from django.shortcuts import render, redirect
from .forms import CalculadoraDoseForm
import math
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv
from .forms import ChatForm

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if GROQ_API_KEY:
    model = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.2,
        groq_api_key=GROQ_API_KEY
    )
else:
    model = None
    print("A chave de API da Groq não foi encontrada. Certifique-se de configurá-la no arquivo .env.")


def pagina_inicial(request):
    form = CalculadoraDoseForm()
       
    if request.method == 'POST':
         form = CalculadoraDoseForm(request.POST)
         if form.is_valid():
            nome = form.cleaned_data['nome']
            request.session['nome'] = nome
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
        'nome': request.session.get('nome'),
        'nivel_saude': request.session.get('nivel_saude'),
        'dose_inicial': request.session.get('dose_inicial'),
        'num_semanas': request.session.get('num_semanas'),
        'tipo_progressao': request.session.get('tipo_progressao'),
        'cronograma': request.session.get('cronograma'),
        'erro_sugestoes': request.session.get('erro_sugestoes'),
        'erro_cronograma': request.session.get('erro_cronograma'),
        'form': CalculadoraDoseForm(),
        'chat_form': ChatForm(),
        'chat_messages': request.session.get('chat_messages', []),
        'mensagem_ia': None,
        'erro_mensagem_ia': None,
    }

    if model:
        nome = request.session.get('nome', 'usuário')
        nivel_saude = request.session.get('nivel_saude', 'desconhecido')
        dose_inicial = request.session.get('dose_inicial', 'desconhecida')
        num_semanas = request.session.get('num_semanas', 'desconhecido')
        tipo_progressao = request.session.get('tipo_progressao', 'desconhecida')
        cronograma = request.session.get('cronograma', [])

        prompt_mensagem = f"""Você deve agir como um assistente de saúde amigável e informativo. O nome do usuário é "{nome}".

Com base nas informações do usuário, o nível de saúde identificado é "{nivel_saude}" e a dose inicial recomendada de Ozempic é "{dose_inicial} mg". O cronograma de tratamento tem um total de {num_semanas} semanas, com uma progressão de dose do tipo "{tipo_progressao}". O cronograma detalhado é o seguinte:
{''.join([f'- Semana {i+1}: {dose}\n' for i, dose in enumerate(cronograma)])}

Por favor, formule uma mensagem para o usuário "{nome}" que inclua:
- Uma saudação amigável.
- A informação sobre o nível de saúde identificado: "{nivel_saude}".
- A dose inicial recomendada: "{dose_inicial} mg".
- O número total de semanas do tratamento: "{num_semanas}".
- O tipo de progressão da dose: "{tipo_progressao}".
- O cronograma detalhado de doses.
- Uma mensagem de acompanhamento curta e motivacional, reforçando a importância da consulta médica, adesão ao tratamento e um estilo de vida saudável. Mantenha um tom profissional e encorajador.
"""
        
        try:
            resposta_ia = model.invoke([HumanMessage(content=prompt_mensagem)])
            context['mensagem_ia'] = resposta_ia.content
        except Exception as e:
            context['erro_mensagem_ia'] = f"Ocorreu um erro ao gerar a mensagem com a IA: {e}"
    else:
        context['erro_mensagem_ia'] = "A funcionalidade de mensagem personalizada com IA não está disponível no momento."

    if not GROQ_API_KEY:
        context['erro_mensagem_ia'] = "A chave de API da Groq não está configurada. Verifique o arquivo .env."
        return render(request, 'exibir_cronograma.html', context)

    if request.method == 'POST':
        if 'enviar_mensagem_chat' in request.POST:
            chat_form = ChatForm(request.POST)
            if chat_form.is_valid():
                user_question = chat_form.cleaned_data['mensagem']
                if model:
                    try:
                        prompt_chat = f"""Você é um assistente útil para um usuário que acabou de receber um cronograma de doses de Ozempic. Responda às perguntas do usuário de forma clara e concisa, sempre lembrando da importância da consulta médica e do acompanhamento profissional. O cronograma do usuário é: {request.session.get('cronograma', [])}. Pergunta do usuário: {user_question}"""
                        response_chat = model.invoke([HumanMessage(content=prompt_chat)])
                        chat_messages = request.session.get('chat_messages', [])
                        chat_messages.append({'user': user_question, 'bot': response_chat.content})
                        request.session['chat_messages'] = chat_messages
                        context['chat_messages'] = chat_messages
                        context['chat_form'] = ChatForm() 
                    except Exception as e:
                        context['erro_chat_ia'] = f"Ocorreu um erro no chat com a IA: {e}"
                else:
                    context['erro_chat_ia'] = "A funcionalidade de chat com IA não está disponível no momento."
            else:
                context['chat_form'] = chat_form 



    return render(request, 'exibir_cronograma.html', context)

def index(request):
    if request.method == 'GET':
     return render(request, 'index.html')
    
    if request.method == 'POST':
     return redirect('pagina_inicial')




















