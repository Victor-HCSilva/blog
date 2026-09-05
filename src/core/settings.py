import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# 1. IDENTIFICAÇÃO DE CAMINHOS
# Localização: projeto/src/core/settings.py
CURRENT_FILE = Path(__file__).resolve()

# Caminho da pasta 'src' (onde estão os apps e o manage.py)
SRC_DIR = CURRENT_FILE.parent.parent

# Caminho da RAIZ do projeto (onde estão .envs, db.sqlite3, static e media)
BASE_DIR = SRC_DIR.parent

# 2. AJUSTE DO PYTHON PATH (O "pulo do gato")
# Isso faz o Django encontrar os apps (main, agenda) mesmo estando dentro de src/
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# 3. CARREGAMENTO DAS VARIÁVEIS DE AMBIENTE
dotenv_path = BASE_DIR / ".envs" / ".env"
load_dotenv(dotenv_path)

# 4. CONFIGURAÇÕES BÁSICAS
SECRET_KEY = os.getenv("SECRET_KEY", "chave-secreta-padrao")

# IMPORTANTE: Converter string do env para booleano real
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

trusted_hosts_raw = (
    "127.0.0.1,localhost,192.168.122.1,10.0.0.108,victoraccount2.pythonanywhere.com"
)


ALLOWED_HOSTS = [host.strip() for host in trusted_hosts_raw.split(",")]

# 5. LOGIN E SESSÃO
LOGIN_URL = "main:login"
LOGIN_REDIRECT_URL = "main:home"
LOGOUT_REDIRECT_URL = "main:home"

# 6. DJANGO AXES
AXES_FAILURE_LIMIT = 5
HOUR = 3600
AXES_COOLOFF_TIME = 200 if DEBUG else int(HOUR / 2)

AXES_RESET_ON_SUCCESS = True  # Reseta as chances ao acertar a senha
AXES_LOCKOUT_PARAMETERS = ["username", "ip_address"]
AXES_THRESHOLD_WINDOW = 24  # Esquece tentativas muito antigas (em horas)

# SESSÕES
SESSION_COOKIE_AGE = 10000 if DEBUG else int(HOUR / 10)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# 7. APPS E MIDDLEWARE
INSTALLED_APPS = [
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "main",
    "axes",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
    "core.middleware.CurrentUserMiddleware",
]

ROOT_URLCONF = "core.urls"

# 8. TEMPLATES (Ajustado para o novo BASE_DIR)
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Agora busca em projeto/src/main/templates
        "DIRS": [SRC_DIR / "main" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# 9. BANCO DE DATOS (Na raiz do projeto)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# 10. ESTÁTICOS E MEDIA
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# 11. AUTENTICAÇÃO
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# INTERNACIONALIZAÇÃO
TIME_ZONE = "America/Sao_Paulo"
LANGUAGE_CODE = "pt-br"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


