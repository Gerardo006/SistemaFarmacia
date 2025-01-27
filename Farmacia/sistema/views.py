from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import LoginForm
from .models import Usuario


# Create your views here.


def home(request):
    return render(request, 'home.html')

def login_views(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():  # Confirmar que el formulario es válido
            user = form.cleaned_data['Usuario']  # Obtener el usuario
            login(request, user)  # Iniciar sesión

            # Verificar el nombre del usuario y redirigir según corresponda
            if Usuario.username == 'admin_user':  # Nombre de usuario específico del administrador
                return redirect('administrador')  # Ruta para administradores
            elif Usuario.username == 'empleado_user':  # Nombre de usuario del empleado
                return redirect('empleado')  # Ruta para empleados
            else:
                return redirect('cliente')  # Ruta para otros usuarios
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def administrador(request):
    return render(request, 'administrador.html')


def empleado(request):
    return render(request, 'empleado.html')


def cliente(request):
    return render(request, 'cliente.html')