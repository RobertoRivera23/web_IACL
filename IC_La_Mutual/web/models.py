from datetime import datetime  # 👈 Importación correcta
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

# --------------------------
# Modelos principales
# --------------------------

# Form Contacto

class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True, null=True)
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Abogado(models.Model):
    nombre = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100)
    descripcion = models.TextField()
    foto = models.ImageField(upload_to='abogados/')

    def __str__(self):
        return self.nombre

class CategoriaServicio(models.Model):
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre

class Servicio(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(null=True, blank=True)
    imagen = models.ImageField(
        upload_to='servicios/',
        null=True,
        blank=True,
        default='images/imagen.jpg'  # Default moved here
    )
    categoria = models.ForeignKey(
        CategoriaServicio,
        on_delete=models.CASCADE,
        default=1  # Asegurar que exista categoría con id=1
    )
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    dni = models.CharField(max_length=8, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)  # 👈 Permitir NULL temporalmente
    telefono = models.CharField(max_length=20)
    direccion = models.TextField(null=True)
    fecha_registro = models.DateTimeField(
        auto_now_add=True,  # 👈 Restaura esta opción
        help_text="Fecha de registro del cliente"
    )
    def __str__(self):
        return f"{self.nombre} ({self.usuario.username})"
    
# --------------------------
# Modelos de operaciones
# --------------------------

class ServicioCliente(models.Model):
    ESTADOS = (
        ('P', 'Pendiente'),
        ('E', 'En proceso'),
        ('C', 'Completado'),
    )
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    honorarios = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Honorarios Acordados"
    )
    fecha_asignacion = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=1, choices=ESTADOS, default='P')
    detalles = models.TextField(blank=True)

    def __str__(self):
        return f"{self.cliente} - {self.servicio}"

# --------------------------
# Modelos complementarios
# --------------------------

class CarouselItem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['orden']
        verbose_name = "Item del Carrusel"

class CategoriaPublicacion(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Publicacion(models.Model):
    titulo = models.CharField(max_length=200)
    imagen = models.ImageField(upload_to='publicaciones/')
    enlace = models.URLField()
    categorias = models.ManyToManyField(CategoriaPublicacion)
    fecha_publicacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.titulo

class Pago(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    referencia = models.CharField(max_length=50)
    metodo = models.CharField(max_length=50)

class Notificacion(models.Model):
    CANALES = (
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
        ('ambos', 'Ambos'),
    )
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    canal = models.CharField(max_length=10, choices=CANALES, default='email')
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notificación para {self.cliente}"

def validate_file_size(value):
    max_size = 5 * 1024 * 1024  # 5MB
    if value.size > max_size:
        raise ValidationError("El tamaño máximo permitido es 5MB")

class DocumentoRequerido(models.Model):
    TIPO_DOCUMENTO = (
        ('DNI', 'Documento de Identidad'),
        ('FACT', 'Factura'),
        ('CONTR', 'Contrato'),
    )
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=5, choices=TIPO_DOCUMENTO)
    descripcion = models.TextField()
    fecha_limite = models.DateField()
    archivo = models.FileField(
        upload_to='documentos_clientes/',
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        null=True,
        blank=True
    )
    completado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.cliente} - {self.get_tipo_display()}"
    
class AuditoriaDocumento(models.Model):
    ACCIONES = (
        ('UPLOAD', 'Subida de archivo'),
        ('STATUS', 'Cambio de estado'),
        ('DELETE', 'Documento eliminado'),
    )

    documento = models.ForeignKey(DocumentoRequerido, on_delete=models.CASCADE)
    accion = models.CharField(max_length=6, choices=ACCIONES)
    detalle = models.JSONField(default=dict)  # Almacena cambios específicos
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_accion_display()} - {self.documento}"