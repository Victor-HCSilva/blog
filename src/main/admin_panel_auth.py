from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse


def admin_required(view_func):
    """
    Decorator para views administrativas.
    Garante que o usuário esteja autenticado no backend e possua status
    de staff (is_staff) ou superusuário (is_superuser).
    
    - Usuários anônimos são redirecionados para a tela de login mantendo o parâmetro 'next'.
    - Usuários comuns autenticados recebem PermissionDenied (HTTP 403 Forbidden).
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            login_url = reverse("main:login")
            return redirect(f"{login_url}?next={request.path}")
        if not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied("Acesso restrito a administradores.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view
