from django.db import models
from django.utils import timezone
from datetime import timedelta


class Municipio(models.Model):
    nome = models.CharField(max_length=120)
    uf = models.CharField(max_length=2)
    endereco_sede = models.CharField(max_length=200, blank=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class EmpresaTransporte(models.Model):
    razao_social = models.CharField(max_length=200)
    nome_fantasia = models.CharField(max_length=150, blank=True)
    cnpj = models.CharField(max_length=18, unique=True)
    endereco = models.CharField(max_length=200, blank=True)

    municipio = models.ForeignKey(
        Municipio,
        on_delete=models.PROTECT,
        related_name='empresas'
    )

    def __str__(self):
        return self.nome_fantasia


class Usuario(models.Model):
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    cpf = models.CharField(max_length=14, unique=True)
    endereco = models.CharField(max_length=200, blank=True)

    saldo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class TipoTicket(models.Model):

    TIPOS = [
        ('avulso', 'Avulso'),
        ('diario', 'Diário'),
        ('semanal', 'Semanal'),
        ('mensal', 'Mensal'),
        ('anual', 'Anual'),
    ]

    nome = models.CharField(max_length=20, choices=TIPOS)

    descricao = models.TextField(blank=True)

    valor = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    duracao_dias = models.PositiveSmallIntegerField()

    janela_integracao_minutos = models.PositiveSmallIntegerField(
        default=60
    )

    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.get_nome_display()


class Ticket(models.Model):

    STATUS = [
        ('ativo', 'Ativo'),
        ('expirado', 'Expirado'),
        ('cancelado', 'Cancelado'),
        ('consumido', 'Consumido'),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='tickets'
    )

    tipo = models.ForeignKey(
        TipoTicket,
        on_delete=models.PROTECT,
        related_name='tickets'
    )

    data_compra = models.DateTimeField(auto_now_add=True)

    valor_pago = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    data_validade = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='ativo'
    )

    def save(self, *args, **kwargs):

        if not self.pk:
            self.valor_pago = self.tipo.valor

            self.data_validade = (
                timezone.now() +
                timedelta(days=self.tipo.duracao_dias)
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.usuario.nome} - {self.tipo.nome}'


class Transporte(models.Model):

    TIPOS = [
        ('parada', 'Parada'),
        ('onibus', 'Ônibus'),
        ('trem', 'Trem'),
    ]

    identificacao = models.CharField(
        max_length=50,
        unique=True
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPOS
    )

    nome = models.CharField(max_length=150)

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )

    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )

    empresa = models.ForeignKey(
        EmpresaTransporte,
        on_delete=models.PROTECT,
        related_name='transportes'
    )

    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.identificacao


class Validador(models.Model):

    TIPOS = [
        ('cartao', 'Cartão'),
        ('celular', 'Celular'),
    ]

    codigo = models.CharField(
        max_length=50,
        unique=True
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPOS
    )

    transporte = models.ForeignKey(
        Transporte,
        on_delete=models.PROTECT,
        related_name='validadores',
        null=True,
        blank=True
    )

    data_instalacao = models.DateField()

    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.codigo


class Validacao(models.Model):

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.PROTECT,
        related_name='validacoes'
    )

    validador = models.ForeignKey(
        Validador,
        on_delete=models.PROTECT,
        related_name='validacoes'
    )

    transporte = models.ForeignKey(
        Transporte,
        on_delete=models.PROTECT,
        related_name='validacoes'
    )

    data_hora = models.DateTimeField(auto_now_add=True)

    dentro_janela_integracao = models.BooleanField(
        default=False
    )

    valor_debitado = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return f'{self.ticket} - {self.data_hora}'