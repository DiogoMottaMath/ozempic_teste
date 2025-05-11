from django.urls import path
from . import views 

urlpatterns = [
    path('pagina_inicial', 
         views.pagina_inicial, 
         name='pagina_inicial'),
    path('exibir_cronograma',
         views.exibir_cronograma,
         name='exibir_cronograma'),
     path('index',
         views.index,
         name='index'),        
]






