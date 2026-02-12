from datetime import datetime
from typing import Optional
from uuid import uuid4

# Importações do FastAPI para criação da API e gerenciamento de respostas
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

# Ferramentas do Pydantic para estruturação de dados 
from pydantic import BaseModel, EmailStr, Field, field_serializer, UUID4

# Inicialização da aplicação FastAPI
app = FastAPI()

class User(BaseModel):
    # model_config define comportamentos globais
    model_config = {
        "extra": "forbid",
    }
    
    # Lista em memória para simular um banco de dados de usuários durante a execução
    __users__ = []
    
    # Definição dos campos com metadados para documentação e validação
    name: str = Field(..., description="Name of the user")
    email: EmailStr = Field(..., description="Email address of the user")
    
    # Listas de UUIDs com limite máximo de 500 itens 
    friends: list[UUID4] = Field(
        default_factory=list, max_items=500, description="List of friends"
    )
    blocked: list[UUID4] = Field(
        default_factory=list, max_items=500, description="List of blocked users"
    )
    
    # kw_only=True garante que campos com valor padrão sejam passados apenas via nome da chave
    signup_ts: Optional[datetime] = Field(
        default_factory=datetime.now, description="Signup timestamp", kw_only=True
    )
    id: UUID4 = Field(
        default_factory=uuid4, description="Unique identifier", kw_only=True
    )

    # Converte o objeto UUID em string ao exportar para o formato JSON da API
    @field_serializer("id", when_used="json")
    def serialize_id(self, id: UUID4) -> str:
        return str(id)

# Rota GET: Retorna a lista completa de usuários armazenados na memória
@app.get("/users", response_model=list[User])
async def get_users() -> list[User]:
    return list(User.__users__)

# Rota POST: Recebe dados brutos, valida via Pydantic e adiciona à lista de usuários
@app.post("/users", response_model=User)
async def create_user(user: User):
    User.__users__.append(user)
    return user

# Rota GET por ID: Busca um usuário específico ou retorna erro 404 caso não exista
@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: UUID4) -> User | JSONResponse:
    try:
        # Busca o primeiro usuário cuja ID coincida com o parâmetro da URL
        return next((user for user in User.__users__ if user.id == user_id))
    except StopIteration:
        # Retorna resposta JSON customizada com código de status de erro
        return JSONResponse(status_code=404, content={"message": "User not found"})

# Função Principal que executa testes automatizados simulando um cliente HTTP
def main() -> None:
    # TestClient permite testar as rotas da API sem precisar subir o servidor manualmente
    with TestClient(app) as client:
      
        # Criação de um loop de 5 usuários para testes
        for i in range(5):
            response = client.post(
                "/users",
                json={"name": f"User {i}", "email": f"example{i}@arjancodes.com"},
            )
            #  Verifica se a API retornou Sucesso (200) e os dados corretos
            assert response.status_code == 200
            assert response.json()["name"] == f"User {i}"
            assert response.json()["id"]

            # Valida se o JSON retornado pela API pode ser convertido de volta para o modelo User
            user = User.model_validate(response.json())
            assert str(user.id) == response.json()["id"]

        # Valida se o endpoint GET retorna exatamente os 5 usuários criados
        response = client.get("/users")
        assert response.status_code == 200
        assert len(response.json()) == 5

        # Testa a criação de um usuário individual e sua recuperação posterior pelo ID
        response = client.post(
            "/users", json={"name": "User 5", "email": "example5@arjancodes.com"}
        )
        user_id = response.json()["id"]
        
        # Valida a busca de um usuário que sabemos que existe
        response = client.get(f"/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "User 5"

        # Testa o cenário de erro: Busca de uma ID aleatória (deve retornar 404)
        response = client.get(f"/users/{uuid4()}")
        assert response.status_code == 404
        assert response.json()["message"] == "User found"     # Erro proposital no assert original para falha

        # Testa a validação automática do Pydantic para e-mails mal formatados (Erro 422)
        response = client.post("/users", json={"name": "User 6", "email": "wrong"})
        assert response.status_code == 422

# Ponto de entrada padrão para execução direta do script de teste
if __name__ == "__main__":
    main()
