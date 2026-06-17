# API de Produtos - FastAPI com PostgreSQL

Uma API RESTful para gerenciamento de produtos construída com FastAPI, SQLAlchemy e PostgreSQL, com testes automatizados completos.

## 📋 Pré-requisitos

- Python 3.13+
- Docker e Docker Compose
- Git

## 🚀 Início Rápido

### 1. Clonar o Repositório

```bash
git clone https://github.com/guilhermerodriguesmain/backend-produtos.git
cd backend-produtos
```

### 2. Criar e Ativar o Ambiente Virtual

```bash
# Windows (PowerShell)
python -m venv env
.\env\Scripts\Activate.ps1

# Linux/macOS
python -m venv env
source env/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
DATABASE_URL=postgresql://usuario:senha@host:porta/nome_do_banco

```

Ajuste as credenciais conforme sua configuração do Docker.

---

## 🐳 Subir o Banco de Dados com Docker

### Usando Docker Compose

```bash
docker-compose up -d
```

Este comando:
- Cria um container PostgreSQL com o serviço rodando em `localhost:5433`
- User: `usuario`
- Password: `senha`
- Database: `produtos_db`
- Banco de teste: `produtos_test`

### Verificar se o Container está rodando

```bash
docker-compose ps
```

### Parar o Container

```bash
docker-compose down
```

### Remover dados do banco

```bash
docker-compose down -v  # Remove volumes também
```

---

## 🧪 Executar os Testes

### Comando Básico

```bash
pytest -v
```

### Comando com Cobertura de Código

```bash
pytest -v --cov=app --cov-report=html
```

### Executar apenas um teste específico

```bash
pytest tests/test_produtos.py::test_criar_produto -v
```

### Executar com parada no primeiro erro

```bash
pytest -v -x
```

---

## 📊 Saída Esperada do Pytest

Ao executar `pytest -v`, você deve ver:

```
============================= test session starts =============================
platform win32 -- Python 3.13.3, pytest-9.1.0, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: d:\backend-produtos
configfile: pytest.ini
plugins: anyio-4.14.0, cov-7.1.0
collected 12 items

tests/test_produtos.py::test_lista_vazia PASSED                           [  8%]
tests/test_produtos.py::test_criar_produto PASSED                         [ 16%]
tests/test_produtos.py::test_listar_produtos PASSED                       [ 25%]
tests/test_produtos.py::test_buscar_produto_por_id PASSED                 [ 33%]
tests/test_produtos.py::test_buscar_produto_id_inexistente PASSED         [ 41%]
tests/test_produtos.py::test_deletar_produto PASSED                       [ 50%]
tests/test_produtos.py::test_deletar_produto_inexistente PASSED           [ 58%]
tests/test_produtos.py::test_deletar_produto_e_confirmar_remocao PASSED   [ 66%]
tests/test_produtos.py::test_criar_produto_payload_invalido[payload0] PASSED [ 75%]
tests/test_produtos.py::test_criar_produto_payload_invalido[payload1] PASSED [ 83%]
tests/test_produtos.py::test_criar_produto_payload_invalido[payload2] PASSED [ 91%]
tests/test_produtos.py::test_isolamento_banco PASSED                      [100%]

========================== 12 passed in 0.45s ==========================
```

### Detalhes dos Testes

| # | Teste | Descrição |
|---|-------|-----------|
| 1 | `test_lista_vazia` | Verifica se a lista de produtos está vazia no início |
| 2 | `test_criar_produto` | Cria um produto e verifica se foi salvo corretamente |
| 3 | `test_listar_produtos` | Lista todos os produtos cadastrados |
| 4 | `test_buscar_produto_por_id` | Busca um produto específico por ID |
| 5 | `test_buscar_produto_id_inexistente` | Retorna 404 ao buscar produto inexistente |
| 6 | `test_deletar_produto` | Deleta um produto com sucesso |
| 7 | `test_deletar_produto_inexistente` | Retorna 404 ao deletar produto inexistente |
| 8 | `test_deletar_produto_e_confirmar_remocao` | Deleta e confirma remoção com GET subsequente |
| 9-11 | `test_criar_produto_payload_invalido` | Testes parametrizados para validação (preco negativo, nome vazio, estoque negativo) |
| 12 | `test_isolamento_banco` | Verifica isolamento entre execuções de testes |

---

## 🔒 Isolamento Entre Testes

O projeto utiliza **banco de dados SQLite em memória** durante os testes para garantir isolamento completo entre cada execução.

### Como Funciona?

#### 1. **Fixture `db()` - Banco de Dados Isolado**

```python
@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    # Cria as tabelas
    Base.metadata.create_all(bind=engine)
    
    db_session = TestingSessionLocal()
    
    try:
        yield db_session
    finally:
        db_session.close()
        # LIMPA TODAS as tabelas após o teste
        Base.metadata.drop_all(bind=engine)
```

**Comportamento:**
- ✅ Cada teste recebe um banco **novo e vazio**
- ✅ Após cada teste, **todas as tabelas são deletadas**
- ✅ Não há contaminação entre testes

#### 2. **Fixture `client()` - Cliente HTTP Isolado**

```python
@pytest.fixture(scope="function")
def client(db: Session) -> TestClient:
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db  # Usa a sessão isolada
        finally:
            pass
    
    # Sobrescreve a dependência get_db
    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    
    yield test_client
    
    # Limpa overrides
    app.dependency_overrides.clear()
```

**Benefícios:**
- Cada teste tem sua própria sessão de banco
- Os overrides são removidos após cada teste
- Testes rodam em paralelo sem conflito

#### 3. **Fluxo Completo de Isolamento**

```
Teste 1                          Teste 2
├─ db.create_all()              ├─ db.create_all()
├─ client.post("/produtos")     ├─ client.post("/produtos")
├─ assert ...                   ├─ assert ...
└─ db.drop_all() ✓              └─ db.drop_all() ✓
   (Limpo!)                        (Limpo!)
   
Teste 3 começa com banco VAZIO ✅
```

---

## 🔧 Estrutura do Projeto

```
backend-produtos/
├── app/
│   ├── __init__.py
│   ├── database.py          # Configuração do SQLAlchemy
│   ├── main.py              # Endpoints da API
│   ├── models.py            # Modelos SQLAlchemy
│   └── schemas.py           # Schemas Pydantic
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Fixtures pytest
│   └── test_produtos.py     # Testes dos endpoints
├── .env                      # Variáveis de ambiente
├── .gitignore
├── docker-compose.yaml      # Configuração Docker
├── requirements.txt         # Dependências Python
└── README.md               # Este arquivo
```

---

## 📦 Dependências Principais

- **FastAPI** - Framework web
- **SQLAlchemy** - ORM para banco de dados
- **Pydantic** - Validação de dados
- **psycopg2** - Driver PostgreSQL
- **pytest** - Framework de testes
- **pytest-cov** - Cobertura de testes
- **uvicorn** - ASGI server

---

## 🚀 Executar a Aplicação

### Modo Desenvolvimento (Local)

```bash
# Em desenvolvimento (com auto-reload)
uvicorn app.main:app --reload

# Em produção
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

A API estará disponível em: `http://localhost:8000`

### Modo Docker (Recomendado)

#### 1. Build da Imagem

```bash
docker build -t api-produtos:latest .
```

#### 2. Executar com Docker Compose (Aplicação + Bancos)

```bash
docker-compose up -d
```

Isto inicia:
- **app** (API FastAPI) em `http://localhost:8000`
- **db** (PostgreSQL) em `localhost:5432`
- **db_test** (PostgreSQL para testes) em `localhost:5433`

#### 3. Parar os Containers

```bash
docker-compose down
```

#### 4. Ver Logs da Aplicação

```bash
docker-compose logs -f app
```

#### 5. Executar Testes dentro do Container

```bash
docker-compose exec app pytest -v
```

### Documentação Interativa

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`


---

## 🐛 Troubleshooting

### Erro: `ModuleNotFoundError: No module named 'app'`

```bash
# Certifique-se que está no diretório raiz
cd backend-produtos

# Ative o ambiente virtual
.\env\Scripts\Activate.ps1  # Windows
source env/bin/activate     # Linux/macOS

# Reinstale dependências
pip install -r requirements.txt
```

### Erro: `DATABASE_URL not defined`

Crie o arquivo `.env` na raiz com a URL do banco:

```env
DATABASE_URL=postgresql://usuario:senha@host:porta/nome_do_banco

```

### Erro: Connection refused (PostgreSQL)

```bash
# Inicie o Docker
docker-compose up -d

# Aguarde 5 segundos para o PostgreSQL estar pronto
# Verifique a conexão
docker-compose ps
```

---

## 📝 Licença

MIT

---

## 👤 Autor

Guilherme Rodrigues - [GitHub](https://github.com/guilhermerodriguesmain/backend-produtos.git)
