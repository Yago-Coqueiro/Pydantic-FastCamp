import enum          
import hashlib      
import re            
from typing import Any, Self     # Any permite qualquer tipo; Self refere-se à instância da própria classe

# Importações específicas do Pydantic para estruturar, validar e exportar modelos
from pydantic import (
    BaseModel,            # Classe base para a criação de modelos de dados 
    EmailStr,             # Validador de strings para o e-mail
    Field,                # Permite configurar metadados, valores padrão e restrições de campos
    field_serializer,     # Decorador que define como um campo deve ser formatado para JSON
    field_validator,      # Decorador para criar funções de validação 
    model_serializer,     # Decorador para controlar a representação final do objeto inteiro
    model_validator,      # Decorador para validações que cruzam dados 
    SecretStr,            # Classe que oculta valores sensíveis em prints e logs
)

# Definição regras de complexidade para senha e restrição de caracteres para o nome
VALID_PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")
VALID_NAME_REGEX = re.compile(r"^[a-zA-Z]{2,}$")

# Enumeração com flags inteiras para gerenciar permissões (0 a 8)
class Role(enum.IntFlag):
    User = 0
    Author = 1
    Editor = 2
    Admin = 4
    SuperAdmin = 8

class User(BaseModel):
    # Campo nome: string simples que passará pelo validador customizado
    name: str = Field(examples=["Example"])
    
    # Campo e-mail: validado pelo Pydantic e bloqueado para alterações após criado (frozen)
    email: EmailStr = Field(
        examples=["user@arjancodes.com"],
        description="The email address of the user",
        frozen=True,
    )
    
    # exclude=True: Campo obrigatório internamente, mas removido de qualquer exportação externa
    password: SecretStr = Field(
        examples=["Password123"], description="The password of the user", exclude=True
    )
    
    # validate_default=True: Garante que o valor '0' (User) também seja processado pelos validadores
    role: Role = Field(
        description="The role of the user",
        examples=[1, 2, 4, 8],
        default=0,
        validate_default=True,
    )

    # Verifica se o nome atende aos requisitos da Regex (letras e tamanho)
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not VALID_NAME_REGEX.match(v):
            raise ValueError(
                "Name is invalid, must contain only letters and be at least 2 characters long"
            )
        return v

    # Age antes da conversão de tipo; útil para normalizar entradas (str para Enum)
    @field_validator("role", mode="before")
    @classmethod
    def validate_role(cls, v: int | str | Role) -> Role:
        # Dicionário de funções lambda para converter dinamicamente o tipo de entrada para Role
        op = {int: lambda x: Role(x), str: lambda x: Role[x], Role: lambda x: x}
        try:
            return op[type(v)](v)
        except (KeyError, ValueError):
            raise ValueError(
                f"Role is invalid, please use one of the following: {', '.join([x.name for x in Role])}"
            )

    # Valida a lógica bruta (ex: senha não pode conter o nome)
    @model_validator(mode="before")
    @classmethod
    def validate_user_pre(cls, v: dict[str, Any]) -> dict[str, Any]:
        if "name" not in v or "password" not in v:
            raise ValueError("Name and password are required")
        if v["name"].casefold() in v["password"].casefold():
            raise ValueError("Password cannot contain name")
        if not VALID_PASSWORD_REGEX.match(v["password"]):
            raise ValueError("Password too weak")
          
        # Converte a senha em hash SHA-256 antes de instanciar o objeto
        v["password"] = hashlib.sha256(v["password"].encode()).hexdigest()
        return v

    # Roda com o objeto já pronto; permite usar 'self' para regras complexas
    @model_validator(mode="after")
    def validate_user_post(self, v: Any) -> Self:
      
        # Regra de Negócio: Restrição de privilégios baseada no nome do usuário
        if self.role == Role.Admin and self.name != "Arjan":
            raise ValueError("Only Arjan can be an admin")
        return self

    # Define que, ao exportar para JSON, a Role apareça como texto (Ex: "Admin")
    @field_serializer("role", when_used="json")
    @classmethod
    def serialize_role(cls, v) -> str:
        return v.name

    # Permite interceptar e alterar a estrutura final do JSON
    @model_serializer(mode="wrap", when_used="json")
    def serialize_user(self, serializer, info) -> dict[str, Any]:
        # Se não houver filtros (include/exclude), retorna apenas um par de campos simplificado
        if not info.include and not info.exclude:
            return {"name": self.name, "role": self.role.name}
        # Caso contrário, utiliza o serializador padrão do Pydantic
        return serializer(self)

def main() -> None:
    # Dados de entrada simulando uma requisição de criação de usuário
    data = {
        "name": "Arjan",
        "email": "example@arjancodes.com",
        "password": "Password123",
        "role": "Admin",
    }
    
    # Conversão do dicionário em objeto User, disparando toda a cadeia de validação
    user = User.model_validate(data)
    
    if user:
        # Gera um dicionário Python 
        print("--- The serializer that returns a dict: ---")
        print(user.model_dump())
        
        # Gera dicionário com tipos compatíveis com JSON 
        print("\n--- The serializer that returns a JSON string (dict mode): ---")
        print(user.model_dump(mode="json"))
        
        # Testando exclusão dinâmica de campos na saída
        print("\n--- The serializer excluding the role: ---")
        print(user.model_dump(exclude=["role"], mode="json"))
        
        # Conversão padrão para dicionário nativo do Python
        print("\n--- The serializer that encodes all values to a dict: ---")
        print(dict(user))

# Verifica se o script está sendo executado como programa principal
if __name__ == "__main__":
    main()
