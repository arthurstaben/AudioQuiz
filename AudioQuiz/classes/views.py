from django.http import HttpResponse, Http404
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
from .models import  Notificacao, Classe, Deck, Card, Mensagem, Arquivo
from .forms import ClasseForm, ArquivoForm, DeckForm, CardForm, MensagemForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.safestring import mark_safe
import json
from django.http import JsonResponse

class ClasseListView(ListView):
    model = Classe
    template_name = 'classes/index.html'

class ClasseDeleteView(DeleteView):
    model = Classe
    template_name = 'classes/delete.html'
    success_url = reverse_lazy('classes:index')

class ClasseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Classe
    form_class = ClasseForm
    template_name = 'classes/update.html'
    success_url = reverse_lazy('classes:index')

    def form_valid(self, form):
        classe = form.save(commit=False)
        classe.save()
        form.save_m2m()  # Salvar alunos selecionados
        # Verifica novos alunos para evitar notificações duplicadas
        novos_alunos = form.cleaned_data['alunos'].exclude(id__in=classe.usuarios.all())
        classe.usuarios.add(self.request.user)  # Adiciona o professor à classe
        self.enviar_notificacao_para_alunos(novos_alunos, classe)
        return super().form_valid(form)

    def enviar_notificacao_para_alunos(self, novos_alunos, classe):
        """Envia notificações apenas para novos alunos convidados"""
        for aluno in novos_alunos:
            Notificacao.objects.create(
                titulo="Convite para a classe",
                mensagem=f"Você foi convidado para a classe '{classe.turma}' de {classe.idioma}.",
                classe=classe,
                usuario=aluno
            )
    def test_func(self):
        # Permitir acesso apenas para professores
        return self.request.user.is_authenticated and self.request.user.tipo == 1

class MensagemDeleteView(DeleteView):
    model = Mensagem
    template_name = 'classes/mural/delete.html'

    def get_object(self, queryset=None):
        # Recupera o objeto Mensagem usando o mensagem_id
        mensagem_id = self.kwargs.get('mensagem_id')
        return get_object_or_404(Mensagem, pk=mensagem_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona o objeto Classe ao contexto
        context['Classe'] = get_object_or_404(Classe, pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        # Redireciona de volta para o mural da classe
        return reverse_lazy('classes:mural', kwargs={'pk': self.kwargs['pk']})

class ClasseMuralView(View):
    def get(self, request, pk):
        classe = get_object_or_404(Classe, pk=pk)
        mensagens = classe.mensagens.filter(resposta_para__isnull=True)  # Apenas mensagens principais
        return render(request, 'classes/mural/index.html', {'Classe': classe, 'mensagens': mensagens})

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
            arquivo.usuario = request.user  # Associa o usuário autenticado
            arquivo.tipo = request.FILES['conteudo'].content_type
            arquivo.conteudo = request.FILES['conteudo'].read()
            arquivo.save()
            return HttpResponseRedirect(reverse_lazy('classes:atividades_index', kwargs={'pk': pk}))
        return render(request, 'classes/atividades/atividade.html', {'form': form, 'Classe': classe})

class AtividadeDeleteView(DeleteView):
    model = Arquivo  # Corrige para deletar o modelo Arquivo (atividade)
    template_name = 'classes/atividades/delete.html'
    
    def get_success_url(self):
        # Retorna para a lista de atividades da classe após a exclusão
        return reverse_lazy('classes:atividades_index', kwargs={'pk': self.object.classe.id})

class AtividadeUpdateView(View):
    def get(self, request, pk):
        # Recupera a atividade pelo ID
        atividade = get_object_or_404(Arquivo, pk=pk)
        form = ArquivoForm(instance=atividade)  # Preenche o formulário com os dados da atividade existente
        return render(request, 'classes/atividades/update.html', {'form': form, 'atividade': atividade})

    def post(self, request, pk):
        # Recupera a atividade pelo ID
        atividade = get_object_or_404(Arquivo, pk=pk)
        form = ArquivoForm(request.POST, request.FILES, instance=atividade)  # Associa o formulário à atividade
        if form.is_valid():
            arquivo = form.save(commit=False)
            
            # Verifica se um novo arquivo foi enviado
            if 'conteudo' in request.FILES:
                arquivo.tipo = request.FILES['conteudo'].content_type
                arquivo.conteudo = request.FILES['conteudo'].read()

            arquivo.save()  # Salva as alterações na atividade
            return HttpResponseRedirect(reverse_lazy('classes:atividades_index', kwargs={'pk': atividade.classe.pk}))

        return render(request, 'classes/atividades/update.html', {'form': form, 'atividade': atividade})

def download_pdf(request, pk):
    # Recupera o arquivo pelo ID
    arquivo = get_object_or_404(Arquivo, pk=pk)

    try:
        # Retorna o conteúdo binário como resposta para download
        response = HttpResponse(arquivo.conteudo, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{arquivo.nome}.pdf"'
        return response
    except Exception as e:
        raise Http404("Erro ao processar o arquivo")

class ClasseFlashcardsView(DetailView):
    model = Classe
    template_name = 'classes/flashcards/index.html'
    context_object_name = 'Classe'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona os decks associados à classe
        classe = self.object  # A classe atual
        context['Classe'] = classe  # Disponibiliza o objeto Classe no contexto
        context['Deck_list'] = Deck.objects.filter(classe=self.object)
        return context

class ClasseFlashcardsCreate(CreateView):
    model = Deck
    form_class = DeckForm
    template_name = 'classes/flashcards/create.html'

    def form_valid(self, form):
        classe = get_object_or_404(Classe, pk=self.kwargs['pk'])
        form.instance.classe = classe
        form.instance.usuario = self.request.user
        form.instance.n_dominados = 0
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Classe'] = get_object_or_404(Classe, pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        return reverse_lazy('classes:flashcards', kwargs={'pk': self.kwargs['pk']})
    
class ClasseFlashcardsDelete(DeleteView):
    model = Deck
    template_name = 'classes/flashcards/delete.html'

    def get_object(self, queryset=None):
        print(f"Classe ID: {self.kwargs['pk']}, Deck ID: {self.kwargs['deck_id']}")
        return get_object_or_404(Deck, pk=self.kwargs['deck_id'], classe_id=self.kwargs['pk'])

    def get_success_url(self):
        # Redireciona para a lista de flashcards após a exclusão
        return reverse_lazy('classes:flashcards', kwargs={'pk': self.kwargs['pk']})
    
class CardCreateView(CreateView):
    model = Card
    form_class = CardForm
    template_name = 'classes/flashcards/cards/create.html'

    def form_valid(self, form):
        deck = get_object_or_404(Deck, pk=self.kwargs['deck_id'])
        form.instance.deck = deck
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deck'] = get_object_or_404(Deck, pk=self.kwargs['deck_id'])
        return context

    def get_success_url(self):
        return reverse_lazy('classes:cards', kwargs={'deck_id': self.kwargs['deck_id']})

class DeckCardsView(DetailView):
    model = Deck
    template_name = 'classes/flashcards/cards/cards.html'
    context_object_name = 'deck'

    def get_object(self, queryset=None):
        return get_object_or_404(Deck, pk=self.kwargs['deck_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Serializa os cards
        cards = Card.objects.filter(deck=self.object).values('id','lado_frente', 'lado_tras')
        context['cards'] = mark_safe(json.dumps(list(cards)))  # Converte em JSON e marca como seguro
        return context

class ClasseCreateView(CreateView):
    model = Classe
    form_class = ClasseForm
    template_name = 'classes/create.html'
    success_url = reverse_lazy('classes:index')

    def form_valid(self, form):
        # Salva a classe sem commit
        classe = form.save(commit=False)
        # Salva a instância da classe
        classe.save()
        # Salva a relação N pra N dos usuários selecionados
        form.save_m2m()
        # Adiciona o usuário logado à relação N pra N como criador/professor
        classe.usuarios.add(self.request.user)
        # Envia notificações para os alunos selecionados
        self.enviar_notificacao_para_alunos(form.cleaned_data['alunos'], classe)
        return super().form_valid(form)

    def enviar_notificacao_para_alunos(self, alunos, classe):
        """Envia notificações para os alunos convidados"""
        for aluno in alunos:
            Notificacao.objects.create(
                titulo="Convite para a classe",
                mensagem=f"Você foi convidado para a classe '{classe.turma}' de {classe.idioma}.",
                classe = classe,
                usuario = aluno
            )

class MensagemCreateView(View):
    def get(self, request, pk, resposta_id=None):
        classe = get_object_or_404(Classe, pk=pk)
        resposta_para = None
        if resposta_id:
            resposta_para = get_object_or_404(Mensagem, pk=resposta_id)
        form = MensagemForm()
        return render(request, 'classes/mural/mensagem.html', {'form': form, 'Classe': classe, 'resposta_para': resposta_para})

    def post(self, request, pk, resposta_id=None):
        classe = get_object_or_404(Classe, pk=pk)
        resposta_para = None
        if resposta_id:
            resposta_para = get_object_or_404(Mensagem, pk=resposta_id)
        form = MensagemForm(request.POST)
        if form.is_valid():
            mensagem = form.save(commit=False)
            mensagem.classe = classe
            mensagem.usuario = request.user
            mensagem.resposta_para = resposta_para
            mensagem.save()
            return HttpResponseRedirect(reverse_lazy('classes:mural', kwargs={'pk': pk}))
        return render(request, 'classes/mural/mensagem.html', {'form': form, 'Classe': classe})

def aceitar_convite(request, notificacao_id):
    # Verifica se o usuário está autenticado
    if not request.user.is_authenticated:
        messages.error(request, "Você precisa estar logado para aceitar o convite.")
        return redirect('accounts:login')

    # Obtém a classe e a notificação
    notificacao = get_object_or_404(Notificacao, id=notificacao_id, usuario=request.user)
    classe = get_object_or_404(Classe, id=notificacao.classe_id)

    # Adiciona o usuário à classe
    classe.usuarios.add(request.user)

    # Marca a notificação como lida
    notificacao.lida = True
    notificacao.save()

    messages.success(request, f"Você agora faz parte da classe '{classe.turma}'.")
    return redirect('classes:index')  # Redireciona para a página inicial ou lista de classes

@login_required
def recusar_convite(request, notificacao_id):
    """
    View para recusar o convite de uma classe.
    """
    # Obtém a notificação
    notificacao = get_object_or_404(Notificacao, id=notificacao_id, usuario=request.user)

    # Exclui a notificação, já que o convite foi recusado
    notificacao.delete()

    # Adiciona uma mensagem de sucesso
    messages.success(request, "Você recusou o convite para a classe.")

    # Redireciona o usuário para uma página apropriada (ex: página inicial ou painel de notificações)
    return redirect('classes:index')  # Substitua pelo nome correto da URL