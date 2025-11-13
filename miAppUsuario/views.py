# miAppUsuario/views.py

from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta 
from django.contrib import messages # ⬅️ Importante para mensajes de éxito/error
from django.contrib.auth.hashers import make_password # ⬅️ Importar para hashear la contraseña

from .models import Usuario 
from .forms import UsuarioForm

# ... (La vista home está bien, la dejamos igual) ...
def home(request):
    # ... (código de la vista home) ...
    siete_dias_atras = timezone.now() - timedelta(days=7)
    
    # Nota: Si tu modelo NO tiene 'fecha_creacion' o 'is_active', estos querysets fallarán.
    # Asumimos que sí existen o los adaptas a tus campos.
    total_registros = Usuario.objects.count()
    
    registros_recientes = Usuario.objects.filter(
        fecha_creacion__gte=siete_dias_atras
    ).count()

    usuarios_activos = Usuario.objects.filter(is_active=True).count()
    
    context = {
        'total_registros': total_registros,
        'registros_recientes': registros_recientes,
        'usuarios_activos': usuarios_activos
    }
    
    return render(request, 'home.html', context)


def create(request):
    if request.method == "POST":
        form = UsuarioForm(request.POST)
        
        if form.is_valid():
            # 1. NO guardamos la contraseña plana. Obtenemos el objeto Model sin guardar.
            usuario = form.save(commit=False)
            
            # 2. Obtenemos la contraseña del formulario limpio.
            password = form.cleaned_data.get('contraseña')
            
            # 3. Hasheamos la contraseña y la asignamos al campo del modelo.
            # ⚠️ Asegúrate de que 'contraseña_hash' es el nombre correcto del campo en tu modelo.
            usuario.contraseña_hash = make_password(password)
            
            # 4. Guardamos el objeto finalmente en la base de datos.
            usuario.save()
            
            # 5. Enviamos un mensaje de éxito
            messages.success(request, 'Usuario creado exitosamente. Puede verlo en la lista de registros.')
            
            # 6. Redirigimos para evitar doble envío de formulario (patrón POST/REDIRECT/GET)
            return redirect('/') # Redirige al home o a una vista de lista
        else:
            # Si el formulario no es válido (ej: contraseñas no coinciden)
            messages.error(request, 'Error al crear el usuario. Por favor, revise los campos marcados.')
    else:
        form = UsuarioForm()

    siete_dias_atras = timezone.now() - timedelta(days=7)
    total_registros = Usuario.objects.count()
    
    registros_recientes = Usuario.objects.filter(
        fecha_creacion__gte=siete_dias_atras
    ).count()

    usuarios_activos = Usuario.objects.filter(is_active=True).count()
    context = {
        'form': form, # Pasamos el objeto formulario (ya sea vacío o con errores)
        'usuarios': Usuario.objects.all(), # Puedes dejar esto, aunque no se usa en el template
        'total_registros': total_registros,
        'registros_recientes': registros_recientes,
        'usuarios_activos': usuarios_activos
    }
    # Renderizamos la plantilla con el formulario
    return render(request, 'create.html', context)

def read(request):
    """Muestra todos los registros de usuarios en una tabla."""
    
    # 1. Obtener todos los usuarios de la base de datos
    # ⚠️ OPTIMIZACIÓN: Utilizamos select_related para obtener los datos de la clave foránea (Pais)
    # en la misma consulta, lo cual es más eficiente.
    usuarios = Usuario.objects.select_related('pais_usuario').all()

    # 2. Replicamos la lógica de los contadores para que la cabecera funcione
    siete_dias_atras = timezone.now() - timedelta(days=7)
    
    context = {
        'usuarios': usuarios, # 👈 Lista de objetos Usuario para la tabla
        'total_registros': Usuario.objects.count(),
        'registros_recientes': Usuario.objects.filter(fecha_creacion__gte=siete_dias_atras).count(),
        'usuarios_activos': Usuario.objects.filter(is_active=True).count()
    }
    
    return render(request, 'read.html', context)

# miAppUsuario/views.py

# ... (tus imports y vistas home, create, read) ...

# 🟢 Vistas PLACEHOLDER (Temporales para evitar errores)
def edit(request, pk):
    # Esto simplemente te devolverá al listado por ahora
    messages.info(request, f"Función de edición para ID {pk} pendiente de implementar.")
    return redirect('read') 

def delete(request, pk):
    # Esto simplemente te devolverá al listado por ahora
    messages.info(request, f"Función de eliminación para ID {pk} pendiente de implementar.")
    return redirect('read')