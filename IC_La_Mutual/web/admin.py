from django.contrib import admin
from .models import Cliente, Servicio, CarouselItem, Publicacion, CategoriaServicio, CategoriaPublicacion, Pago, Notificacion, DocumentoRequerido, ServicioCliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'telefono', 'direccion')
    search_fields = ('usuario__username', 'telefono')

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'activo')
    list_filter = ('categoria', 'activo')  # Corregido: quitado 'estado'
    fieldsets = (
        (None, {
            'fields': ('nombre', 'categoria', 'activo')
        }),
        ('Detalles del Servicio', {
            'fields': ('descripcion', 'imagen'),
            'classes': ('collapse',)
        }),
    )
    search_fields = ('nombre', 'descripcion')

@admin.register(ServicioCliente)
class ServicioClienteAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'servicio', 'honorarios', 'estado', 'fecha_asignacion')
    list_filter = ('estado', 'servicio__categoria')  # Filtro por relación
    list_editable = ('estado',)
    raw_id_fields = ('cliente', 'servicio')
    date_hierarchy = 'fecha_asignacion'
    fieldsets = (
        (None, {
            'fields': ('cliente', 'servicio')
        }),
        ('Acuerdo Económico', {
            'fields': ('honorarios', 'fecha_asignacion'),
            'description': "Detalles financieros del servicio"
        }),
        ('Seguimiento', {
            'fields': ('estado', 'detalles'),
            'classes': ('collapse',)
        })
    )

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'fecha', 'monto', 'metodo')
    list_filter = ('metodo', 'fecha')
    search_fields = ('referencia', 'cliente__usuario__username')

@admin.register(CategoriaServicio)
class CategoriaServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(CarouselItem)
class CarouselAdmin(admin.ModelAdmin):
    list_display = ('title', 'orden', 'activo')
    list_editable = ('orden', 'activo')
    ordering = ('orden',)

@admin.register(CategoriaPublicacion)
class CategoriaPublicacionAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Publicacion)
class PublicacionAdmin(admin.ModelAdmin):
    filter_horizontal = ('categorias',)
    list_display = ('titulo', 'fecha_publicacion', 'enlace')
    list_filter = ('categorias',)
    date_hierarchy = 'fecha_publicacion'

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'mensaje_corto', 'canal', 'leida', 'fecha')
    list_filter = ('canal', 'leida')
    date_hierarchy = 'fecha'
    
    def mensaje_corto(self, obj):
        return f"{obj.mensaje[:50]}..." if len(obj.mensaje) > 50 else obj.mensaje
    mensaje_corto.short_description = "Mensaje"

@admin.register(DocumentoRequerido)
class DocumentoRequeridoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'tipo', 'completado', 'fecha_limite')
    list_filter = ('tipo', 'completado')
    search_fields = ('cliente__usuario__username', 'descripcion')
    date_hierarchy = 'fecha_limite'