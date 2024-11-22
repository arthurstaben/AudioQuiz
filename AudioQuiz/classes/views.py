from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.conf import settings
from datetime import datetime
import os, shutil
from django.views.generic import TemplateView, View
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.contrib.auth import login
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import  Classe, Matricula, Deck, Card, Mensagem, Arquivo
from .forms import ClasseForm, ArquivoForm, MatriculaForm, DeckForm, CardForm, MensagemForm

class ClasseListView(ListView):
    model = Classe
    template_name = 'classes/index.html'
    context_object_name = 'Classe_list'

class ClasseDeleteView(DeleteView):
    model = Classe
    template_name = 'classes/delete.html'
    success_url = reverse_lazy('classes:index')

class ClasseMuralView(DetailView):
    model = Classe
    template_name = 'classes/mural/index.html'
    context_object_name = 'Classe'

class ClasseAtividadesView(DetailView):
    model = Classe
    template_name = 'classes/atividades/index.html'
    context_object_name = 'Classe'

class AtividadeCreateView(View):
    def get(self, request, pk):
        classe = get_object_or_404(Classe, pk=pk)# Garante que a Classe existe
        form = ArquivoForm()
        return render(request, 'classes/atividades/atividade.html', {'form': form, 'Classe': classe})

    def post(self, request, pk):
        classe = get_object_or_404(Classe, pk=pk)
        form = ArquivoForm(request.POST, request.FILES)
        if form.is_valid():
            arquivo = form.save(commit=False)
            arquivo.classe = classe
            arquivo.tipo = request.FILES['conteudo'].content_type
            arquivo.conteudo = request.FILES['conteudo'].read()
            arquivo.save()
            return HttpResponseRedirect(reverse_lazy('classes:atividades_index', kwargs={'pk': pk}))
        return render(request, 'classes/atividades/atividade.html', {'form': form, 'Classe': classe})

class ClasseFlashcardsView(DetailView):
    model = Classe
    template_name = 'classes/flashcards/index.html'
    context_object_name = 'Classe'

class ClasseCreateView(CreateView):
    model = Classe
    form_class = ClasseForm
    template_name = 'classes/create.html'
    success_url = reverse_lazy('classes:index')


class MensagemCreateView(View):
    def get(self, request, pk):
        # Obter a classe pelo PK
        classe = get_object_or_404(Classe, pk=pk)
        form = MensagemForm()
        return render(request, 'classes/mural/mensagem.html', {'form': form, 'Classe': classe})

    def post(self, request, pk):
        # Obter a classe pelo PK
        classe = get_object_or_404(Classe, pk=pk)
        form = MensagemForm(request.POST)
        if form.is_valid():
            # Salvar a mensagem associando à classe
            mensagem = form.save(commit=False)
            mensagem.classe = classe
            mensagem.save()
            # Redirecionar para o mural após a criação
            return HttpResponseRedirect(reverse_lazy('classes:mural', kwargs={'pk': pk}))
        # Reexibir o formulário com erros, se inválido
        return render(request, 'classes/mural/mensagem.html', {'form': form, 'Classe': classe})

