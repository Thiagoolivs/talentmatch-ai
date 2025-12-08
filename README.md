# TalentMatch AI

Sistema Inteligente de Matching de Talentos com Vagas

---

## Sobre o Projeto

O **TalentMatch AI** e uma plataforma completa de recrutamento que utiliza Inteligencia Artificial para conectar candidatos as melhores oportunidades de emprego. O sistema analisa habilidades, experiencia, localizacao e pretensao salarial para encontrar matches perfeitos entre candidatos e vagas.

### Principais Diferenciais

- **Matching Inteligente**: Algoritmo ponderado que considera multiplos fatores
- **Chatbot com IA**: Assistente virtual para analise de curriculos e orientacao de carreira
- **Recomendacao de Cursos**: Identifica gaps de habilidades e sugere capacitacoes
- **Sistema Multi-Usuario**: Candidatos, Empresas e Administradores com permissoes distintas

---

## Indice

1. [Funcionalidades](#funcionalidades)
2. [Tecnologias Utilizadas](#tecnologias-utilizadas)
3. [Requisitos do Sistema](#requisitos-do-sistema)
4. [Instalacao](#instalacao)
5. [Configuracao](#configuracao)
6. [Executando o Projeto](#executando-o-projeto)
7. [Estrutura do Projeto](#estrutura-do-projeto)
8. [Tipos de Usuario](#tipos-de-usuario)
9. [Algoritmo de Matching](#algoritmo-de-matching)
10. [API REST](#api-rest)
11. [Comandos de Gerenciamento](#comandos-de-gerenciamento)
12. [Variaveis de Ambiente](#variaveis-de-ambiente)
13. [Deploy em Producao](#deploy-em-producao)
14. [Solucao de Problemas](#solucao-de-problemas)

---

## Funcionalidades

### Para Candidatos
- Cadastro e gerenciamento de perfil profissional
- Upload de curriculo (PDF)
- Busca e filtragem de vagas
- Candidatura a vagas com acompanhamento de status
- Visualizacao de vagas recomendadas por IA
- Chat com empresas sobre candidaturas
- Cursos recomendados para gaps de habilidades
- Chatbot IA para orientacao de carreira

### Para Empresas
- Cadastro com validacao de CNPJ
- Criacao e gerenciamento de vagas
- Visualizacao de candidatos recomendados
- Gerenciamento de candidaturas (status, feedback)
- Sistema de mensagens com candidatos
- Dashboard com metricas de recrutamento

### Para Administradores
- Dashboard completo com estatisticas do sistema
- Verificacao/aprovacao de empresas cadastradas
- Gerenciamento de usuarios (ativar/desativar/excluir)
- Sistema de resolucao de problemas reportados
- Modo de manutencao do site
- Logs de auditoria de acoes administrativas

### Sistema de Cursos
- Catalogo de cursos com licoes estruturadas
- Acompanhamento de progresso
- Suporte a video-aulas
- Recomendacoes personalizadas baseadas em gaps

### Chatbot com IA
- Integracao com Groq API (LLaMA 3.3 70B)
- Analise de curriculos
- Dicas de carreira personalizadas
- Fallback para sistema local quando API indisponivel

---

## Tecnologias Utilizadas

### Backend
| Tecnologia | Versao | Descricao |
|------------|--------|-----------|
| Python | 3.11+ | Linguagem principal |
| Django | 5.2 | Framework web |
| Django REST Framework | 3.16 | API REST |
| Django Filter | 25.2 | Filtragem de querysets |
| Gunicorn | 23.0 | Servidor WSGI para producao |
| WhiteNoise | 6.11 | Servir arquivos estaticos |

### Inteligencia Artificial / Machine Learning
| Tecnologia | Descricao |
|------------|-----------|
| Scikit-learn | Vetorizacao TF-IDF para matching de skills |
| Groq API | LLM para chatbot (LLaMA 3.3 70B) |
| NumPy | Computacao numerica |
| Pandas | Manipulacao de dados |

### Frontend
| Tecnologia | Descricao |
|------------|-----------|
| Tailwind CSS | Framework CSS (via CDN) |
| Chart.js | Graficos interativos nos dashboards |
| JavaScript Vanilla | Interatividade (AJAX, polling) |

### Banco de Dados
| Ambiente | Tecnologia |
|----------|------------|
| Desenvolvimento | SQLite |
| Producao | PostgreSQL |

---

## Requisitos do Sistema

- Python 3.11 ou superior
- pip ou uv (gerenciador de pacotes)
- Git
- Navegador moderno (Chrome, Firefox, Edge, Safari)

### Opcional
- PostgreSQL (para producao)
- Chave API da Groq (para chatbot IA)

---

## Instalacao

### 1. Clonar o Repositorio

```bash
git clone https://github.com/Thiagoolivs/talentmatch-ai.git
cd talentmatch-ai
```

### 2. Criar Ambiente Virtual

**Linux/macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar Dependencias

**Com pip:**
```bash
pip install -r requirements.txt
```

**Com uv (mais rapido):**
```bash
uv sync
```

### 4. Executar Migracoes do Banco de Dados

```bash
python manage.py migrate
```

### 5. Coletar Arquivos Estaticos

```bash
python manage.py collectstatic --noinput
```

### 6. Criar Usuario Administrador

```bash
python manage.py create_admin
```

Isso cria o usuario:
- **Usuario:** `administrador`
- **Senha:** `TalentMatch2025`

### 7. Carregar Dados Iniciais (Opcional)

```bash
# Carregar skills canonicas (66 habilidades)
python manage.py seed_skills

# Carregar cursos de exemplo (5 cursos com licoes)
python manage.py seed_courses
```

---

## Configuracao

### Variaveis de Ambiente

Crie um arquivo `.env` ou configure as variaveis de ambiente:

| Variavel | Obrigatorio | Descricao | Valor Padrao |
|----------|-------------|-----------|--------------|
| `SESSION_SECRET` | Sim (prod) | Chave secreta do Django | Chave insegura para dev |
| `GROQ_API_KEY` | Nao | Chave da API Groq para chatbot IA | - |
| `DEBUG` | Nao | Modo debug (True/False) | True |
| `ADMIN_ACCESS_CODE` | Nao | Codigo para acesso admin alternativo | tm2025admin |

### Configuracao do Banco de Dados

**Desenvolvimento (SQLite - padrao):**
Nenhuma configuracao necessaria.

**Producao (PostgreSQL):**
Configure a variavel `DATABASE_URL` ou edite `talentmatch/settings.py`.

---

## Executando o Projeto

### Desenvolvimento

```bash
python manage.py runserver 0.0.0.0:5000
```

Acesse: `http://localhost:5000`

### Producao

```bash
gunicorn --bind=0.0.0.0:5000 --reuse-port talentmatch.wsgi:application
```

### No Replit

O projeto ja esta configurado. Basta clicar em "Run".

---

## Estrutura do Projeto

```
talentmatch-ai/
├── accounts/                 # Autenticacao e perfis de usuario
│   ├── management/commands/  # Comandos: create_admin, seed_skills
│   ├── migrations/           # Migracoes do banco
│   ├── models.py             # User, CandidateProfile, CompanyProfile
│   ├── views.py              # Login, registro, perfil
│   ├── forms.py              # Formularios com validacao
│   ├── middleware.py         # Manutencao, redirecionamentos
│   └── skill_normalizer.py   # Normalizacao de habilidades
│
├── jobs/                     # Sistema de vagas
│   ├── models.py             # Job, Application, ApplicationStatusHistory
│   ├── views.py              # CRUD de vagas, candidaturas
│   ├── forms.py              # Formularios de vagas
│   └── filters.py            # Filtros de busca
│
├── match/                    # Algoritmo de matching
│   ├── utils.py              # Logica de matching ponderado
│   └── views.py              # Endpoints de recomendacao
│
├── courses/                  # Sistema de cursos
│   ├── management/commands/  # Comando: seed_courses
│   ├── models.py             # Course, Lesson, UserCourse
│   └── views.py              # Listagem, detalhes, progresso
│
├── chatbot/                  # Chatbot com IA
│   ├── ai_engine.py          # Integracao Groq API
│   ├── models.py             # ChatSession, ChatMessage
│   └── views.py              # Interface do chat
│
├── dashboard/                # Dashboards
│   └── views.py              # Dashboard admin, candidato, empresa
│
├── messaging/                # Sistema de mensagens
│   ├── models.py             # Conversation, Message
│   └── views.py              # Chat AJAX
│
├── api/                      # REST API
│   ├── serializers.py        # Serializadores DRF
│   ├── views.py              # ViewSets
│   └── permissions.py        # Permissoes customizadas
│
├── core/                     # Paginas estaticas
│   └── views.py              # Home, sobre, contato
│
├── templates/                # Templates HTML
│   ├── base.html             # Template base
│   ├── accounts/             # Login, registro, perfil
│   ├── jobs/                 # Vagas, candidaturas
│   ├── courses/              # Cursos, licoes
│   ├── dashboard/            # Dashboards
│   ├── chatbot/              # Interface do chat
│   └── messaging/            # Mensagens
│
├── talentmatch/              # Configuracoes do projeto
│   ├── settings.py           # Configuracoes Django
│   ├── urls.py               # URLs principais
│   └── wsgi.py               # Entrada WSGI
│
├── staticfiles/              # Arquivos estaticos coletados
├── media/                    # Uploads (curriculos, logos)
├── manage.py                 # CLI Django
├── requirements.txt          # Dependencias pip
├── pyproject.toml            # Configuracao do projeto
└── README.md                 # Este arquivo
```

---

## Tipos de Usuario

### Candidato (`candidate`)
- Pode criar e editar seu perfil
- Pode buscar e se candidatar a vagas
- Pode visualizar vagas recomendadas
- Pode enviar mensagens para empresas (se tiver candidatura)
- Pode acessar cursos e acompanhar progresso
- Pode usar o chatbot IA

### Empresa (`company`)
- Precisa de aprovacao do admin para funcionalidades completas
- Pode criar e gerenciar vagas (apos aprovacao)
- Pode visualizar candidatos recomendados
- Pode gerenciar candidaturas recebidas
- Pode enviar mensagens para candidatos

### Administrador (`admin`)
- Acesso total ao sistema
- Dashboard com metricas completas
- Aprovacao/rejeicao de empresas
- Gerenciamento de usuarios
- Resolucao de problemas reportados
- Controle do modo de manutencao

---

## Algoritmo de Matching

O sistema usa um algoritmo de matching ponderado que considera:

| Fator | Peso | Descricao |
|-------|------|-----------|
| Habilidades | 50% | Matching exato + similaridade TF-IDF |
| Experiencia | 25% | Comparacao anos requeridos vs candidato |
| Localizacao | 15% | Match cidade/estado |
| Salario | 10% | Compatibilidade pretensao vs oferta |

### Calculo de Score

```
Score Final = (Skills * 0.50) + (Experience * 0.25) + (Location * 0.15) + (Salary * 0.10)
```

O resultado e uma porcentagem de 0% a 100% indicando o nivel de compatibilidade.

---

## API REST

A API REST segue os padroes do Django REST Framework.

### Endpoints Disponiveis

| Endpoint | Metodos | Descricao |
|----------|---------|-----------|
| `/api/users/` | GET, POST | Gerenciamento de usuarios |
| `/api/vagas/` | GET, POST, PUT, DELETE | CRUD de vagas |
| `/api/candidaturas/` | GET, POST, PUT | Gerenciamento de candidaturas |
| `/api/courses/` | GET | Catalogo de cursos |
| `/api/match/` | GET | Resultados de matching |
| `/api/chat/` | GET, POST | Sessoes de chat |

### Autenticacao

A API usa autenticacao baseada em sessao do Django.

### Paginacao

Resultados paginados com 10 itens por pagina por padrao.

---

## Comandos de Gerenciamento

### Criar Administrador
```bash
python manage.py create_admin
```
Cria usuario `administrador` com senha `TalentMatch2025`.

### Carregar Skills Canonicas
```bash
python manage.py seed_skills
```
Carrega 66 habilidades pre-definidas para normalizacao.

### Carregar Cursos de Exemplo
```bash
python manage.py seed_courses
```
Carrega 5 cursos com licoes estruturadas:
- Logica de Programacao (6 licoes)
- Banco de Dados e SQL (6 licoes)
- Desenvolvimento Web com Django (6 licoes)
- Excel e VBA para Negocios (5 licoes)
- Python para Ciencia de Dados (5 licoes)

### Coletar Arquivos Estaticos
```bash
python manage.py collectstatic --noinput
```

### Criar Migracoes
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Variaveis de Ambiente

### Obrigatorias para Producao

| Variavel | Descricao |
|----------|-----------|
| `SESSION_SECRET` | Chave secreta Django (minimo 50 caracteres) |

### Opcionais

| Variavel | Descricao | Padrao |
|----------|-----------|--------|
| `DEBUG` | Ativa modo debug | `True` |
| `GROQ_API_KEY` | Chave API Groq para chatbot IA | - |
| `ADMIN_ACCESS_CODE` | Codigo para acesso admin alternativo | `tm2025admin` |
| `DATABASE_URL` | URL de conexao PostgreSQL | SQLite local |

---

## Deploy em Producao

### Checklist de Producao

1. [ ] Definir `SESSION_SECRET` com chave forte
2. [ ] Definir `DEBUG=False`
3. [ ] Configurar banco de dados PostgreSQL
4. [ ] Executar `collectstatic`
5. [ ] Configurar servidor HTTPS
6. [ ] Configurar backups do banco de dados

### Deploy no Replit

1. O projeto ja esta configurado para deploy
2. Clique em "Deploy" no Replit
3. O sistema usara Gunicorn automaticamente

### Comando de Producao

```bash
gunicorn --bind=0.0.0.0:5000 --reuse-port -w 4 talentmatch.wsgi:application
```

---

## Solucao de Problemas

### Erro: "Acesso indisponivel no momento"

**Causa:** Usuario administrador nao existe no banco de dados.

**Solucao:**
```bash
python manage.py create_admin
```

### Erro de CSRF ao fazer login

**Causa:** Dominio nao esta na lista de origens confiaveis.

**Solucao:** Adicione seu dominio em `CSRF_TRUSTED_ORIGINS` no `settings.py`:
```python
CSRF_TRUSTED_ORIGINS = [
    'https://seu-dominio.com',
    'http://localhost:5000',
]
```

### Chatbot nao responde com IA

**Causa:** Chave `GROQ_API_KEY` nao configurada ou invalida.

**Solucao:** Configure a variavel de ambiente `GROQ_API_KEY` com uma chave valida da Groq.

### Arquivos estaticos nao carregam

**Causa:** Arquivos estaticos nao foram coletados.

**Solucao:**
```bash
python manage.py collectstatic --noinput
```

### Empresa nao consegue criar vagas

**Causa:** Empresa ainda nao foi aprovada pelo administrador.

**Solucao:** Um administrador deve aprovar a empresa em Dashboard > Empresas.

---

## Acesso Administrativo Alternativo

Alem do login padrao, existe um acesso alternativo para administradores:

1. Na pagina de login, clique em "Suporte Tecnico" (link discreto no final)
2. Digite o codigo de acesso: `tm2025admin`
3. Voce sera redirecionado para o dashboard administrativo

**Nota:** O codigo pode ser alterado via variavel de ambiente `ADMIN_ACCESS_CODE`.

---

## Contribuicao

1. Fork o repositorio
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudancas (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

## Licenca

Este projeto esta sob a licenca MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

## Contato

- **Repositorio:** [github.com/Thiagoolivs/talentmatch-ai](https://github.com/Thiagoolivs/talentmatch-ai)
- **Desenvolvedor:** Thiago Oliveira

---

**TalentMatch AI** - Conectando Talentos a Oportunidades com Inteligencia Artificial
