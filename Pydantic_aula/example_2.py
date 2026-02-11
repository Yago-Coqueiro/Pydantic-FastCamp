import enum
import hashlib
import re
from typing import Any

# Importação de ferramentas de validação e estruturação do Pydantic
from pydantic import (
    BaseModel,          # Classe que concede ferramentas de validação à classe User
    EmailStr,           # Validador rigoroso de endereços de e-mail
    Field,              # Permite definir metadados (exemplos, descrições) e restrições
    field_validator,    # Decorador para criar lógica de validação em um campo específico
    model_validator,    # Decorador para validar a relação entre múltiplos campos do objeto
    SecretStr,          # Tipo que protege dados sensíveis contra vazamentos em logs/prints
    ValidationError,    # Classe de erro padrão do Pydantic para capturar falhas de dados
)

# Definição de padrões Regex para garantir formatos específicos de texto (nome e senha)
VALID_PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")
VALID_NAME_REGEX = re.compile(r"^[a-zA-Z]{2,}$")

# Enumeração para níveis de acesso, facilitando o controle de permissões no sistema
class Role(enum.IntFlag):
    Author = 1
    Editor = 2
    Admin = 4
    SuperAdmin = 8

class User(BaseModel):
    # Campo obrigatório: deve ser string e seguir a lógica do field_validator abaixo
    name: str = Field(examples=["Arjan"])
    
    # E-mail validado automaticamente; frozen=True impede alteração após a criação
    email: EmailStr = Field(
        examples=["user@arjancodes.com"],
        description="The email address of the user",
        frozen=True,     
    )
    
    # Senha mascarada pelo SecretStr para segurança do desenvolvedor
    password: SecretStr = Field(
        examples=["Password123"], description="The password of the user"
    )
    
    # Cargo do usuário; default=None torna o campo opcional na entrada dos dados
    role: Role = Field(
        default=None, description="The role of the user", examples=[1, 2, 4, 8]
    )

    # Validador de campo: garante que o nome tenha apenas letras e no mínimo 2 caracteres
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not VALID_NAME_REGEX.match(v):
            raise ValueError(
                "Name is invalid, must contain only letters and be at least 2 characters long"
            )
        return v # Retorna o valor validado para o Pydantic continuar o processo

    # Validador 'before': trata a entrada antes do Pydantic tentar converter o tipo do dado
    @field_validator("role", mode="before")
    @classmethod
    def validate_role(cls, v: int | str | Role) -> Role:
      
        # Mapeamento para aceitar Role como número, nome (string) ou o próprio objeto Role
        op = {int: lambda x: Role(x), str: lambda x: Role[x], Role: lambda x: x}
        try:
            return op[type(v)](v)
        except (KeyError, ValueError):
            raise ValueError(
                f"Role is invalid, please use one of the following: {', '.join([x.name for x in Role])}"
            )

    # Validador de modelo global: executa verificações que dependem de mais de um campo
    @model_validator(mode="before")
    @classmethod
    def validate_user(cls, v: dict[str, Any]) -> dict[str, Any]:
      
        # Checa existência manual de campos obrigatórios antes da conversão final
        if "name" not in v or "password" not in v:
            raise ValueError("Name and password are required")
        
        # Regra de Negócio: Impede que a senha contenha o nome do usuário (case-insensitive)
        if v["name"].casefold() in v["password"].casefold():
            raise ValueError("Password cannot contain name")
        
        # Validação de complexidade da senha via Regex 
        if not VALID_PASSWORD_REGEX.match(v["password"]):
            raise ValueError(
                "Password is invalid, must contain 8 characters, 1 uppercase, 1 lowercase, 1 number"
            )
        
        # Segurança: Transforma a senha em hash SHA-256 (irreversevel) antes de salvar no objeto
        v["password"] = hashlib.sha256(v["password"].encode()).hexdigest()
        return v # Retorna o dicionário de dados processado

def validate(data: dict[str, Any]) -> None:
    try:
        # model_validate: O ponto de entrada que dispara todos os validadores acima
        user = User.model_validate(data)
        print(f"Validated User Object: {user}")
      
    except ValidationError as e:
        # Exibe o erro detalhado formatado pelo Pydantic caso qualquer regra falhe
        print("User is invalid:")
        print(e)

def main() -> None:
    # Estrutura de teste com múltiplos cenários (sucesso e falhas propositais)
    test_data = dict(
        good_data={ # Dados perfeitos
            "name": "Arjan",
            "email": "example@arjancodes.com",
            "password": "Password123",
            "role": "Admin",
        },
        bad_role={ # Testa a conversão de string inválida para Enum
            "name": "Arjan",
            "email": "example@arjancodes.com",
            "password": "Password123",
            "role": "Programmer",
        },
        bad_data={ # Testa formato de e-mail e senha curta
            "name": "Arjan",
            "email": "bad email",
            "password": "bad",
        },
        duplicate={ # Testa a lógica do model_validator (senha igual ao nome)
            "name": "Arjan",
            "email": "example@arjancodes.com",
            "password": "Arjan123",
        },
    )

    # Loop para processar e imprimir cada caso de teste
    for example_name, data in test_data.items():
        print(f"--- TEST CASE: {example_name} ---")
        validate(data)
        print()

# Padrão Python para garantir que o script de teste só execute se o arquivo for chamado diretamente
if __name__ == "__main__":
    main()
