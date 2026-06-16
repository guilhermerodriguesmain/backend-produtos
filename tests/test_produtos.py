# Teste de lista de produtos vazia
def test_lista_vazia(client):
    response = client.get("/produtos")

    assert response.status_code == 200
    assert response.json() == []
    