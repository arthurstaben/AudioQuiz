from django.db import models
from accounts.models import Usuario

class Classe(models.Model):
    turma = models.CharField(max_length=255)
    idioma = models.CharField(max_length=255)
    poster = models.ImageField(upload_to='classes/', blank=True, null=True)

    def __str__(self):
        return self.turma


class Matricula(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.usuario} - {self.classe}"


class Deck(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    nome = models.CharField(max_length=255)
    idioma = models.CharField(max_length=255)
    n_cartoes = models.IntegerField()
    n_dominados = models.IntegerField()
    n_aprender = models.IntegerField()

    def __str__(self):
        return self.nome


class Card(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    lado_frente = models.CharField(max_length=255)
    lado_tras = models.CharField(max_length=255)
    dica_1 = models.CharField(max_length=255, blank=True, null=True)
    dica_2 = models.CharField(max_length=255, blank=True, null=True)
    dica_3 = models.CharField(max_length=255, blank=True, null=True)
    n_revisoes = models.IntegerField()
    maduro = models.BooleanField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_ultima_revisao = models.DateTimeField()

    def __str__(self):
        return self.lado_frente


class Mensagem(models.Model):
    TIPOS = (
        ('TEXTO', 'Texto'),
        ('IMAGEM', 'Imagem'),
        ('VIDEO', 'Vídeo'),
    )
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    conteudo = models.TextField(max_length=1000)
    data_envio = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=10, choices=TIPOS)

    def __str__(self):
        return f"Mensagem de {self.usuario}"

class Arquivo(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    nome = models.CharField(max_length=255)  # Nome do arquivo
    tipo = models.CharField(max_length=50, default='PDF')  # Tipo do arquivo (ex: application/pdf)
    conteudo = models.BinaryField(default=b'')# Armazena o conteúdo binário do arquivo
    data_upload = models.DateTimeField(auto_now_add=True, null=True)  # Data de envio

    def __str__(self):
        return self.nome
