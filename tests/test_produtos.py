"""
foram criados 10 testes cobrindo os cenários obrigatórios, incluindo a validação de isolamento do banco entre execuções e testes parametrizados para payloads inválidos.

os testes agora cobrem os seguintes cenários:
1- test_lista_vazia 
2- test_criar_produto
3- test_listar_produtos 
4- test_buscar_produto_por_id
5- test_buscar_produto_id_inexistente 
6- test_deletar_produto
7- test_deletar_produto_inexistente 
8- test_deletar_produto_e_confirmar_remocao
9- test_criar_produto_payload_invalido 10- test_isolamento_banco
"""

# Teste de lista de produtos vazia
def test_lista_vazia(client):
    response = client.get("/produtos")

    assert response.status_code == 200
    assert response.json() == []

# Teste de criação de produto e persistência
def test_criar_produto(client):
    payload = {
        "nome": "Teclado Mecânico",
        "preco": 299.90,
        "estoque": 5,
        "ativo": True
    }
    response = client.post("/produtos", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["nome"] == payload["nome"]
    assert data["preco"] == payload["preco"]
    assert data["estoque"] == payload["estoque"]
    assert data["ativo"] == payload["ativo"]
    
    # Verificar persistência no banco
    get_response = client.get(f"/produtos/{data['id']}")   
    assert get_response.status_code == 200
    assert get_response.json() == data
    
# Teste de listagem após criação
def test_listar_produtos(client, produto_existente):
    response = client.get("/produtos")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == produto_existente["id"]
    assert data[0]["nome"] == produto_existente["nome"]
    assert data[0]["preco"] == produto_existente["preco"]
    assert data[0]["estoque"] == produto_existente["estoque"]
    assert data[0]["ativo"] == produto_existente["ativo"]
    
# Teste de busca por id - sucesso
def test_buscar_produto_por_id(client, produto_existente):
    response = client.get(f"/produtos/{produto_existente['id']}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == produto_existente["id"]
    assert data["nome"] == produto_existente["nome"]
    assert data["preco"] == produto_existente["preco"]
    assert data["estoque"] == produto_existente["estoque"]
    assert data["ativo"] == produto_existente["ativo"]
    
# Teste de busca por id - produto inexistente
def test_buscar_produto_id_inexistente(client):
    response = client.get("/produtos/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Produto não encontrado"}
    
# Teste de deleção de produto - sucesso
def test_deletar_produto(client, produto_existente):
    response = client.delete(f"/produtos/{produto_existente['id']}")

    assert response.status_code == 204
    
    # Confirmar remoção com GET subsequente
    get_response = client.get(f"/produtos/{produto_existente['id']}")
    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "Produto não encontrado"}

# Teste de deleção de produto inexistente
def test_deletar_produto_inexistente(client):
    response = client.delete("/produtos/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Produto não encontrado"}
    
# Teste deletar produto e confirmar remoção com GET subsequente
def test_deletar_produto_e_confirmar_remocao(client, produto_existente):
    delete_response = client.delete(f"/produtos/{produto_existente['id']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/produtos/{produto_existente['id']}")
    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "Produto não encontrado"}

# Teste parametrizado para payloads inválidos
import pytest
from fastapi.testclient import TestClient
@pytest.mark.parametrize("payload", [
    {"nome": "Produto Teste", "preco": -10.0, "estoque": 5, "ativo": True},
    {"nome": "", "preco": 10.0, "estoque": 5, "ativo": True},
    {"nome": "Produto Teste", "preco": 10.0, "estoque": -5, "ativo": True}
])
def test_criar_produto_payload_invalido(client, payload):
    response = client.post("/produtos/", json=payload)
    assert response.status_code == 422
    
# Teste para validar isolamento do banco entre execuções
def test_isolamento_banco(client):
    response = client.get("/produtos")
    assert response.status_code == 200
    assert response.json() == []

