from django.db import models

# Create your models here.
class Usuario(models.Model):
    nome = models.CharField(max_length=255)
    sobrenome = models.CharField(max_length=255)
    usuario = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    senha = models.CharField(max_length=255)
    tipo = models.BooleanField()  # True ou False

    def __str__(self):
        return f"{self.nome} {self.sobrenome}"