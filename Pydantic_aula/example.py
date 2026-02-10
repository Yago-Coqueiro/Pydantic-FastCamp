from enum import auto, IntFlag
from typing import Any

# Importação dos componentes principais do Pydantic
from pydantic import (
    BaseModel,        # Classe base para criar modelos de dados
    EmailStr,         # Tipo especial que valida se a string é um e-mail real
    Field,            # Permite adicionar metadados e restrições aos campos
    SecretStr,        # Protege dados sensíveis (senhas) para não aparecerem em logs/prints
    ValidationError,  # Exceção disparada quando a validação falha
)

# Definindo permissões usando IntFlag 
# Permite que um usuário tenha múltiplas funções ao mesmo tempo (ex: Author e Editor)
class Role(IntFlag):
    Author = auto()
    Editor = auto()
    Developer = auto()
    Admin = Author | Editor | Developer

# O Modelo Pydantic define a "forma" que os dados devem ter
class User(BaseModel):
    # Field ajuda na documentação automática 
    name: str = Field(examples=["Arjan"])
    
    # EmailStr valida automaticamente se existe '@' e um domínio válido
    # frozen=True impede que o e-mail seja alterado após o objeto ser criado
    email: EmailStr = Field(
        examples=["example@arjancodes.com"],
        description="The email address of the user",
        frozen=True,
    )
    
    # SecretStr garante que tentativas de impressão de senhas resultem em valores censurados
    password: SecretStr = Field(
        examples=["Password123"], description="The password of the user"
    )
    
    # Define o cargo do usuário usando o Enum Role
    role: Role = Field(default=None, description="The role of the user")

# Função de Validação: Transforma um dicionário comum em um objeto 'User' validado
def validate(data: dict[str, Any]) -> None:
    try:
      
        # model_validate checa tipos e regras
        user = User.model_validate(data)
        print(f"User is valid: {user}")
    except ValidationError as e:
      
        # Se os dados forem ruins (ex: e-mail sem @), o Pydantic explica exatamente o erro
        print("User is invalid")
        for error in e.errors():
            print(f"Error in field {error['loc']}: {error['msg']}")

def main() -> None:
    # Dados que seguem as regras do modelo
    good_data = {
        "name": "Arjan",
        "email": "example@arjancodes.com",
        "password": "Password123",
    }
    
    # Dados que quebram as regras (e-mail inválido e falta o campo 'name')
    bad_data = {"email": "<bad data>", "password": "<bad data>"}

    print("--- Testing Good Data ---")
    validate(good_data)
    
    print("\n--- Testing Bad Data ---")
    validate(bad_data)
  
# Garante que main() só rode se o arquivo for executado diretamente
if __name__ == "__main__":
    main()
