from django import forms
from .models import Usuario

# Formulário para o modelo Usuario
class UsuarioForm(forms.ModelForm):
    senha = forms.CharField(widget=forms.PasswordInput, label="Senha")  # Campo de senha com input seguro

    class Meta:
        model = Usuario
        fields = ['nome', 'sobrenome', 'usuario', 'email', 'senha', 'tipo']
        labels = {
            'nome': 'Nome',
            'sobrenome': 'Sobrenome',
            'usuario': 'Usuário',
            'email': 'E-mail',
            'tipo': 'Professor',
        }
        widgets = {
            'tipo': forms.CheckboxInput(),
        }
