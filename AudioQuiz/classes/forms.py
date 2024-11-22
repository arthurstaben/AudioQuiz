from django import forms
from .models import Classe, Matricula, Deck, Card, Mensagem, Arquivo

# Formulário para o modelo Classe
class ClasseForm(forms.ModelForm):
    class Meta:
        model = Classe
        fields = ['turma', 'idioma', 'poster']
        labels = {
            'turma': 'Turma',
            'idioma': 'Idioma',
            'poster': 'Poster',
        }


# Formulário para o modelo Matricula
class MatriculaForm(forms.ModelForm):
    class Meta:
        model = Matricula
        fields = ['usuario', 'classe']
        labels = {
            'usuario': 'Usuário',
            'classe': 'Classe',
        }


# Formulário para o modelo Deck
class DeckForm(forms.ModelForm):
    class Meta:
        model = Deck
        fields = ['usuario', 'classe', 'nome', 'idioma', 'n_cartoes', 'n_dominados', 'n_aprender']
        labels = {
            'usuario': 'Usuário',
            'classe': 'Classe',
            'nome': 'Nome do Deck',
            'idioma': 'Idioma',
            'n_cartoes': 'Número de Cartões',
            'n_dominados': 'Cartões Dominados',
            'n_aprender': 'Cartões a Aprender',
        }


# Formulário para o modelo Card
class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['deck', 'lado_frente', 'lado_tras', 'dica_1', 'dica_2', 'dica_3', 'n_revisoes', 'maduro', 'data_ultima_revisao']
        labels = {
            'deck': 'Deck',
            'lado_frente': 'Lado Frente',
            'lado_tras': 'Lado Trás',
            'dica_1': 'Dica 1',
            'dica_2': 'Dica 2',
            'dica_3': 'Dica 3',
            'n_revisoes': 'Número de Revisões',
            'maduro': 'Maduro',
            'data_ultima_revisao': 'Última Revisão',
        }
        widgets = {
            'data_ultima_revisao': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


# Formulário para o modelo Mensagem
class MensagemForm(forms.ModelForm):
    class Meta:
        model = Mensagem
        fields = ['usuario', 'conteudo', 'tipo']
        labels = {
            'usuario': 'Usuário',
            'conteudo': 'Conteúdo',
            'tipo': 'Tipo',
        }
        widgets = {
            'conteudo': forms.Textarea(attrs={'rows': 4, 'cols': 50}),
            'tipo': forms.Select(choices=Mensagem.TIPOS),
        }

class ArquivoForm(forms.ModelForm):
    class Meta:
        model = Arquivo
        fields = ['usuario', 'nome']  
        labels = {
            'usuario': 'Usuário',}
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Digite o nome do arquivo'}),
        }