# Django Blog

Uma plataforma de publicação moderna construída com **Django 5**, com suporte a modo escuro/claro, sistema de autenticação, painel administrativo próprio e proteção avançada com django-axes.

---

## 📋 Funcionalidades

### Blog Público
- Feed de publicações com busca integrada
- Detalhamento de posts com sistema de comentários
- Diferenciação de posts publicados e rascunhos
- Autenticação de usuários (login, cadastro, logout)
- Proteção contra força bruta com django-axes (bloqueio por tentativas inválidas)

### Painel Administrativo (`/admin-panel/`)
Área exclusiva para usuários `is_staff` ou `is_superuser`:
- **Dashboard** com estatísticas: total de posts, publicados, rascunhos, comentários e usuários
- **Gerenciamento de Posts**: listar, filtrar, visualizar, editar, publicar, despublicar e excluir
- **Gerenciamento de Comentários**: listar, filtrar por status, visualizar e excluir
- **Gerenciamento de Usuários**: listar, visualizar e ativar/desativar usuários com segurança
- Todas as ações destrutivas exigem confirmação e são protegidas por CSRF

---

## 🛠️ Stack Técnica

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12+ / Django 5.2 |
| Frontend | Twind (Tailwind via CDN) + FontAwesome + Django Templates |
| Banco de Dados | SQLite (desenvolvimento) |
| Autenticação | Django Auth + django-axes (bloqueio por brute force) |
| Upload de Imagens | Pillow |
| CORS | django-cors-headers |

---

## 🚀 Getting Started (Linux)

### Pré-requisitos
- Python 3.12+
- Git

### Instalação

```bash
# 1. Clonar o repositório
git clone <este-repositorio>
cd blog

# 2. Criar e ativar o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .envs/.env.example .envs/.env  # edite conforme necessário

# 5. Aplicar migrações
python src/manage.py migrate

# 6. Criar superusuário (acesso ao painel administrativo)
python src/manage.py createsuperuser

# 7. Iniciar o servidor de desenvolvimento
python src/manage.py runserver
```

Ou via Makefile:

```bash
make install    # cria venv e instala dependências
make migrate    # aplica migrações
make runserver  # inicia o servidor
```

---

## 🗂️ Estrutura do Projeto

```
blog/
├── .envs/               # Variáveis de ambiente (não commitadas)
├── docs/                # Documentação adicional
├── media/               # Uploads (imagens de capa dos posts)
├── staticfiles/         # Arquivos estáticos coletados
├── src/
│   ├── core/            # Configurações e URLs raiz do projeto
│   │   ├── settings.py
│   │   └── urls.py
│   └── main/            # App principal do blog
│       ├── models.py            # Post, Comment
│       ├── views.py             # Views públicas do blog
│       ├── admin_panel_views.py # Views do painel administrativo
│       ├── admin_panel_urls.py  # Rotas do painel (/admin-panel/)
│       ├── admin_panel_auth.py  # Decorator @admin_required
│       ├── forms.py             # Formulários públicos
│       ├── admin_panel_forms.py # Formulários administrativos
│       ├── urls.py              # Rotas públicas
│       ├── tests.py             # Testes do blog público (23 testes)
│       ├── test_admin_panel.py  # Testes do painel admin (19 testes)
│       └── templates/
│           ├── base.html        # Layout base do blog
│           ├── blog/            # Templates públicos
│           └── admin_panel/     # Templates do painel administrativo
├── requirements.txt
└── Makefile
```

---

## 🔑 Variáveis de Ambiente

Crie o arquivo `.envs/.env` com base nas configurações em `src/core/settings.py`:

```env
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
```

---

## 🔐 Controle de Acesso

| Rota | Acesso |
|---|---|
| `/` | Público |
| `/post/<slug>/` | Público (rascunhos apenas para o autor) |
| `/cadastro/`, `/login/` | Público |
| `/posts/novo/`, `/meus-posts/` | Requer autenticação |
| `/admin-panel/` e sub-rotas | Requer `is_staff` ou `is_superuser` |
| `/admin/` | Django Admin nativo |

---

## 🧪 Testes

```bash
# Executar todos os testes
make test
# ou
.venv/bin/python src/manage.py test main

# Verificar integridade do sistema
.venv/bin/python src/manage.py check
```

- **42 testes** cobrindo models, views públicas, CRUD de posts/comentários, controle de acesso, CSRF e integridade do painel administrativo.

---

## 📦 Comandos Úteis (Makefile)

```bash
make help          # Lista todos os comandos disponíveis
make install       # Instala dependências em um novo venv
make migrate       # Aplica migrações ao banco
make makemigrations # Gera novas migrações
make createsuperuser # Cria superusuário
make test          # Executa os testes
make collectstatic # Coleta arquivos estáticos
```

---

## 🌐 Deploy (PythonAnywhere)

O projeto está configurado para funcionar em `victoraccount2.pythonanywhere.com`.  
Certifique-se de ajustar `ALLOWED_HOSTS` em `settings.py` e configurar as variáveis de ambiente antes do deploy.
