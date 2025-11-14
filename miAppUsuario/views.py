# miAppUsuario/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta 
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages # ⬅️ Importante para mensajes de éxito/error
from django.contrib.auth.hashers import make_password, check_password # ⬅️ Importar para hashear la contraseña
from django.contrib.auth.decorators import login_required

# Importar la librería pandas
import pandas as pd 
# Importar el error para manejar duplicados/violaciones de constraints en la DB
from django.db import IntegrityError

from .models import Usuario, Rol
from miAppCalificacion.models import Pais
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
        # 🟢 Lógica de Carga Masiva (Bulk Upload)
        if 'excel_file' in request.FILES and request.POST.get('bulk_upload') == 'true':
            excel_file = request.FILES['excel_file']
            
            # Verificar extensión del archivo
            if not excel_file.name.endswith(('.xlsx', '.xls')):
                messages.error(request, 'El archivo debe ser de formato Excel (.xlsx o .xls).')
                return redirect('usuarios:create')
            
            try:
                # Cargar datos desde Excel (asume la primera hoja)
                df = pd.read_excel(excel_file)
                df = df.fillna('')
                
                # Columnas esperadas en el archivo Excel
                # ⚠️ Mantenemos 'nombre' y 'apellido' aquí, pero mapeamos a first_name/last_name
                columnas_esperadas = ['nombre', 'apellido', 'email', 'telefono', 'edad', 'rol_id', 'pais_id', 'contraseña']
                
                if not all(col in df.columns for col in columnas_esperadas):
                    messages.error(request, 'El archivo Excel debe contener las columnas: nombre, apellido, email, telefono, edad, rol_id, pais_id, contraseña.')
                    return redirect('usuarios:create')

                usuarios_creados = 0
                errores = []
                
                for index, row in df.iterrows():
                    try:
                        rol_obj = Rol.objects.get(pk=row['rol_id'])
                        pais_obj = Pais.objects.get(pk=row['pais_id'])
                        
                        # Crear el objeto Usuario SIN guardar aún
                        nuevo_usuario = Usuario(
                            # 🟢 Mapeamos 'nombre' y 'apellido' del Excel a los campos de AbstractUser:
                            first_name=row['nombre'],
                            last_name=row['apellido'],
                            email=row['email'],
                            telefono=row['telefono'],
                            edad=row['edad'],
                            rol_usuario=rol_obj,
                            pais_usuario=pais_obj,
                            is_active=True, 
                            fecha_creacion=timezone.now()
                        )
                        
                        # 🟢 Usar set_password para hashear y asignar la contraseña
                        nuevo_usuario.set_password(row['contraseña'])
                        
                        # Guardar la instancia completa
                        nuevo_usuario.save()
                        
                        usuarios_creados += 1
                        
                    except Rol.DoesNotExist:
                        errores.append(f"Fila {index + 2}: El Rol con ID {row['rol_id']} no existe.")
                    except Pais.DoesNotExist:
                        errores.append(f"Fila {index + 2}: El País con ID {row['pais_id']} no existe.")
                    except IntegrityError:
                        errores.append(f"Fila {index + 2}: Error de integridad (ej. email duplicado) para {row['email']}.")
                    except Exception as e:
                        errores.append(f"Fila {index + 2}: Error desconocido al crear usuario. {e}")
                
                # ... (Mensajes finales de la carga masiva) ...

                if usuarios_creados > 0:
                    messages.success(request, f'✅ Carga masiva exitosa: {usuarios_creados} usuarios creados.')
                
                if errores:
                    error_msg = f'⚠️ Se crearon {usuarios_creados} usuarios. {len(errores)} errores encontrados: '
                    for i, error in enumerate(errores):
                        if i < 5:
                            error_msg += f'({error}) '
                        else:
                            error_msg += f'...y {len(errores) - 5} errores más.'
                            break
                    messages.error(request, error_msg)

                return redirect('usuarios:read')
            
            except Exception as e:
                messages.error(request, f'❌ Error al procesar el archivo Excel: {e}')
                return redirect('usuarios:create')
                
        # 🟢 Lógica de Creación Individual (Formulario)
        form = UsuarioForm(request.POST)
        
        if form.is_valid():
            usuario = form.save(commit=False)
            password = form.cleaned_data.get('contraseña')
            
            usuario.set_password(password)
            
            usuario.save()
            
            messages.success(request, 'Usuario creado exitosamente. Puede verlo en la lista de registros.')
            
            return redirect('usuarios:read')
        else:
            messages.error(request, 'Error al crear el usuario. Por favor, revise los campos marcados.')
    else:
        form = UsuarioForm()

    # ... (resto de la función create) ...
    siete_dias_atras = timezone.now() - timedelta(days=7)
    total_registros = Usuario.objects.count()
    
    registros_recientes = Usuario.objects.filter(
        fecha_creacion__gte=siete_dias_atras
    ).count()

    usuarios_activos = Usuario.objects.filter(is_active=True).count()
    context = {
        'form': form,
        'usuarios': Usuario.objects.all(),
        'total_registros': total_registros,
        'registros_recientes': registros_recientes,
        'usuarios_activos': usuarios_activos
    }
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
# 🟢 Vistas PLACEHOLDER (Temporales para evitar errores)
def edit(request, pk):
    """
    Vista para actualizar un usuario existente, manteniendo la lógica de hasheo
    de contraseña solo si se proporciona una nueva.
    """
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == "POST":
        form = UsuarioForm(request.POST, instance=usuario)
        
        if form.is_valid():
            usuario_instance = form.save(commit=False)
            
            # 4. LÓGICA DE ACTUALIZACIÓN DE CONTRASEÑA
            password = form.cleaned_data.get('contraseña')
            
            if password:
                # 🟢 Solo si se proporciona una nueva contraseña, la hasheamos.
                # ❌ usuario_instance.contraseña_hash = make_password(password)
                usuario_instance.set_password(password)
            
            # 5. Guardar los datos del usuario (incluyendo o no la nueva contraseña hasheada)
            usuario_instance.save()
            
            # ⚠️ Nota: Si corregiste models.py, 'nombre' y 'apellido' ahora son first_name/last_name
            # Debes usar los nombres de campo de AbstractUser:
            messages.success(request, f'¡El usuario "{usuario.first_name} {usuario.last_name}" ha sido actualizado exitosamente!') 
            
            return redirect('usuarios:read')
        else:
            messages.error(request, 'Error al actualizar el usuario. Por favor, revise los campos marcados.')
    
    else:
        form = UsuarioForm(instance=usuario)

    # ... (resto de la función edit) ...
    siete_dias_atras = timezone.now() - timedelta(days=7)
    
    context = {
        'form': form,
        'usuario': usuario,
        'total_registros': Usuario.objects.count(),
        'registros_recientes': Usuario.objects.filter(fecha_creacion__gte=siete_dias_atras).count(),
        'usuarios_activos': Usuario.objects.filter(is_active=True).count()
    }
    
    return render(request, 'edit.html', context)

# -----------------------------------------------------------
# Vista de Eliminación (DELETE)
# -----------------------------------------------------------
def delete(request, pk):
    """
    Vista para mostrar la pantalla de confirmación de eliminación 
    y para ejecutar la eliminación del registro de usuario por su PK.
    """
    # 1. Obtener el usuario o lanzar 404
    # Necesitamos la instancia del usuario en ambos casos (GET y POST)
    usuario = get_object_or_404(Usuario, pk=pk)

    # 2. Manejar la petición POST (Confirmación de eliminación)
    if request.method == "POST":
        
        # Guardamos el nombre antes de eliminarlo para usarlo en el mensaje de éxito
        nombre_completo = f"{usuario.first_name} {usuario.last_name}"
        
        try:
            # 2.1. Ejecutar la eliminación
            usuario.delete()
            
            # 2.2. Enviar mensaje de éxito y redirigir
            messages.success(request, f'✅ ¡El usuario "{nombre_completo}" ha sido **eliminado permanentemente** del sistema!')
            return redirect('usuarios:read') # Redirige al listado de usuarios
            
        except Exception as e:
            # En caso de error (ej: restricciones de clave foránea no manejadas)
            messages.error(request, f'❌ Error al intentar eliminar el usuario "{nombre_completo}". Detalle: {e}')
            return redirect('usuarios:read')

    # 3. Manejar la petición GET (Mostrar la pantalla de confirmación)
    
    # Replicar la lógica de contadores para el template base (home.html)
    siete_dias_atras = timezone.now() - timedelta(days=7)
    
    context = {
        'usuario': usuario, # 👈 Objeto Usuario necesario para el título del template delete.html
        # Contadores para el template base (home.html)
        'total_registros': Usuario.objects.count(),
        'registros_recientes': Usuario.objects.filter(fecha_creacion__gte=siete_dias_atras).count(),
        'usuarios_activos': Usuario.objects.filter(is_active=True).count()
    }
    
    # 4. Renderizar el template de confirmación
    return render(request, 'delete.html', context)

# -----------------------------------------------------------
# 1. VISTA DE INICIO DE SESIÓN (LOGIN)
# -----------------------------------------------------------
# Asegúrate de importar esto arriba:
# from django.contrib.auth import authenticate, login 

def login_view(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        email_ingresado = request.POST.get('email')
        password_ingresada = request.POST.get('contraseña')

        # 🟢 Usamos authenticate, que busca el usuario por email y verifica la contraseña hasheada.
        usuario = authenticate(request, email=email_ingresado, password=password_ingresada)
        
        if usuario is not None:
            if usuario.is_active:
                # El login exitoso disparará la actualización de last_login.
                login(request, usuario)
                messages.success(request, '¡Inicio de sesión exitoso!')
                # Redirige a la URL configurada para el dashboard
                return redirect('admin_dashboard') 
            else:
                messages.error(request, 'Su cuenta está inactiva. Contacte al administrador.')
                
        else:
            messages.error(request, 'Credenciales inválidas. Revise su email y contraseña.')
            
    return render(request, 'login.html')


# -----------------------------------------------------------
# 2. VISTA DE SELECCIÓN DE TAREAS (ADMIN DASHBOARD)
# -----------------------------------------------------------
@login_required(login_url='login') 
def admin_dashboard(request):
    rol_actual = request.user.rol_usuario.nombre if hasattr(request.user, 'rol_usuario') and request.user.rol_usuario else None
    
    if rol_actual == 'Administrador':
        context = {
            # 🟢 CORRECCIÓN: Usar first_name en lugar de nombre
            'nombre_usuario': request.user.first_name, 
            'rol': rol_actual,
        }
        # 🟢 CORRECCIÓN: Renderizar 'home.html' (según tu estructura de archivos)
        return render(request, 'home.html', context) 
        
    else:
        messages.warning(request, f'Acceso denegado. Su rol ({rol_actual if rol_actual else "No definido"}) no está autorizado para esta área.')
        logout(request)
        return redirect('login')


# -----------------------------------------------------------
# 3. VISTA DE CERRAR SESIÓN (LOGOUT)
# -----------------------------------------------------------
def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')