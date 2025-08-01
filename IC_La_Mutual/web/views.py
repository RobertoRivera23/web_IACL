from django.shortcuts import render, redirect
from .models import Abogado, Servicio, Cliente, ServicioCliente, Pago, CarouselItem, Publicacion, DocumentoRequerido, Notificacion  
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.conf import settings



def index(request):
    if request.method == 'POST' and 'contacto_submit' in request.POST:
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono', '')
        mensaje = request.POST.get('mensaje')
        
        asunto = f"Nuevo mensaje de contacto de {nombre}"
        cuerpo = f"""
        Nombre: {nombre}
        Email: {email}
        Teléfono: {telefono}
        Mensaje:
        {mensaje}
        """
        
        try:
            send_mail(
                asunto,
                cuerpo,
                settings.EMAIL_HOST_USER,
                [settings.CONTACT_EMAIL],
                fail_silently=False,
            )
            messages.success(request, '¡Mensaje enviado con éxito!')
        except Exception as e:
            messages.error(request, f'Error al enviar el mensaje: {str(e)}')
        
        # Redirección corregida
        return redirect('inicio')  # Ahora que está definido en urls.py
    
    context = {
        'carousel_items': CarouselItem.objects.filter(activo=True).order_by('orden'),
        'servicios': Servicio.objects.select_related('categoria').all(),
        'publicaciones': Publicacion.objects.prefetch_related('categorias').order_by('-fecha_publicacion')[:6],
    }
    return render(request, 'index.html', context)

def sobre_nosotros(request):
    abogados = Abogado.objects.all()
    return render(request, 'sobre_nosotros.html', {'abogados': abogados})

def servicios(request):
    context = {
        'servicios': Servicio.objects.select_related('categoria').all(),
    }
    return render(request, 'servicios.html', context)

def blog(request):
    context = {
        'publicaciones': Publicacion.objects.prefetch_related('categorias').order_by('-fecha_publicacion')[:6],
    }
    return render(request, 'blog.html', context)

def contacto(request):
    return render(request, 'contacto.html')

@login_required
def dashboard_cliente(request):
    
    return render(request, 'clientes/dashboard.html', context)


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('area_clientes')  # Asegúrate de que 'area_clientes' esté en urls.py
        else:
            return render(request, 'login.html', {'error': 'Usuario o contraseña incorrectos'})
    return render(request, 'login.html')



@login_required
def area_clientes(request):
    try:
        cliente = request.user.cliente  # Acceso directo
    except Cliente.DoesNotExist:
        messages.success(request, "❌ Acceso restringido: No tienes un perfil de cliente válido")
        logout(request)  # Cierra la sesión
        return redirect('login')  # Redirige al login

    # Paginación de documentos
    documentos_list = DocumentoRequerido.objects.filter(cliente=cliente).order_by('-fecha_limite')
    documentos_paginator = Paginator(documentos_list, 5)  # 5 por página
    page_docs = request.GET.get('page_docs', 1)

    # Paginación de notificaciones
    notificaciones_list = Notificacion.objects.filter(cliente=cliente).order_by('-fecha')
    notif_paginator = Paginator(notificaciones_list, 5)
    page_notif = request.GET.get('page_notif', 1)

    try:
        documentos = documentos_paginator.page(page_docs)
        notificaciones = notif_paginator.page(page_notif)
    except (PageNotAnInteger, EmptyPage):
        documentos = documentos_paginator.page(1)
        notificaciones = notif_paginator.page(1)


    # Obtener servicios contratados (no del catálogo)
    servicios_contratados = ServicioCliente.objects.filter(cliente=cliente)
    
    # Cálculo de deuda total (honorarios pendientes)
    deuda_total = sum(
        sc.honorarios for sc in servicios_contratados 
        if sc.estado in ['P', 'E']  # Pendiente o En Proceso
    )

    # Obtener documentos y pagos
    documentos = DocumentoRequerido.objects.filter(cliente=cliente)
    pagos = Pago.objects.filter(cliente=cliente)
    notificaciones = Notificacion.objects.filter(cliente=cliente, leida=False)

    # Progreso de documentos
    total_docs = documentos.count()
    docs_completos = documentos.filter(completado=True).count()
    progreso = (docs_completos / total_docs * 100) if total_docs > 0 else 0

    # Manejo de subida de documentos
    if request.method == 'POST' and 'archivo' in request.FILES:
        doc_id = request.POST.get('doc_id')
        documento = get_object_or_404(DocumentoRequerido, id=doc_id, cliente=cliente)
        
        # Validación adicional
        if documento.completado:
            messages.warning(request, "Este documento ya fue completado")
            return redirect('area_clientes')
            
        documento.archivo = request.FILES['archivo']
        documento.completado = True
        documento.save()
        messages.success(request, "✅ Documento subido exitosamente")
        return redirect('area_clientes')

    context = {
        'documentos': documentos,
        'cliente': cliente,
        'servicios': servicios_contratados,
        'pagos': pagos,
        'documentos_pendientes': documentos.filter(completado=False),
        'notificaciones': notificaciones,
        'deuda_total': deuda_total,
        'progreso': round(progreso, 1),
    }
    return render(request, 'area_clientes.html', context)

@login_required
def logout_view(request):
    logout(request)
    return redirect('index.html')

@login_required
def historial_documento(request, documento_id):
    documento = get_object_or_404(DocumentoRequerido, id=documento_id, cliente=request.user.cliente)
    historial = AuditoriaDocumento.objects.filter(documento=documento).order_by('-fecha')
    
    return render(request, 'historial.html', {
        'documento': documento,
        'historial': historial
    })
