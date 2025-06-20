from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

urlpatterns = [
    
    path('', views.index, name='inicio'),
    path('sobre_nosotros/', views.sobre_nosotros, name='sobre_nosotros'),
    path('servicios/', views.servicios, name='servicios'),
    path('blog/', views.blog, name='blog'),
    path('contacto/', views.contacto, name='contacto'),
    path('login/', views.login_view, name='login'),
    path('area_clientes/', views.area_clientes, name='area_clientes'),
    path('historial//<int:documento_id>/', views.historial_documento, name='historial'),
    path('logout/', LogoutView.as_view(next_page='inicio'), name='logout'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)