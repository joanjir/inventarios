import os
from typing import re
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, EmailMultiAlternatives
from email.mime.image import MIMEImage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.models import Group, User
from django.contrib.auth.forms import UserChangeForm
from django.http import JsonResponse
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect
User = get_user_model()



@never_cache
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
             # Redirigir a la plantilla del administrador para superusuarios
            if request.user.is_superuser:
                print('pase por aca')
                return redirect('dashboard') 
            else:
                # Redirigir a la plantilla del usuarios
                print('entre aqui')
                return redirect('dashboard')
        else:
            # Mostrar un mensaje de error si las credenciales son inválidas
            messages.warning(request, "Usuario o contraseña incorrecta.")
            return render(request, 'registration/login.html')
    else:
        if request.user.is_authenticated:
            # Redireccionar al usuario si ya ha iniciado sesión
            if request.user.is_superuser:
                print('pase por aca')
                return redirect('dashboard') 
            # Redirigir a la plantilla del administrador para superusuarios
            else:
                print('entre aqui')
                return redirect('dashboard')
        else:
            response = render(request, 'registration/login.html')
            # Configurar una cookie para evitar el caché de las páginas después de cerrar sesión
            response.set_cookie('session_cleared', 'true')
            return response


def logout_view(request):
    try:
        logout(request)
        message = "Has cerrado sesión exitosamente."

        messages.success(request, message, extra_tags='Éxito')
    except Exception as e:
        # Aquí puedes realizar acciones específicas en caso de que se produzca una excepción al llamar a logout
        message = "Ha ocurrido un error al cerrar sesión."
        messages.success(request, message, extra_tags='Error')

    # Redirigir a la página de inicio de sesión con el mensaje en la URL
    return redirect('login')
