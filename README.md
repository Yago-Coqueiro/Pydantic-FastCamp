# Validação de Dados com Pydantic 

Este repositório é dedicado ao estudo do **Pydantic**, explorando como a biblioteca transforma o Python em uma ferramenta poderosa para garantir a integridade de dados e a segurança de tipos.

## Conteúdo do Repositório

### 1. Pydantic_Aula (Scripts example_1 a 4)
Uma jornada técnica sobre as capacidades fundamentais da biblioteca, evoluindo em complexidade.
* **Fundamentos:** Definição de esquemas com `BaseModel`, uso de `Field` para metadados e restrições de valor.
* **Validação Avançada:** Implementação de `field_validator` e `model_validator` para regras de negócio complexas e cruzamento de dados.
* **Transformação de Dados:** Uso de Enums, tipos especializados (`UUID4`, `EmailStr`, `SecretStr`) e serializadores customizados para controle de saída JSON.
* **Contexto de Uso:** Demonstração prática de como o Pydantic serve de motor para o **FastAPI**, garantindo que apenas dados válidos cheguem aos endpoints através do `response_model`.

### 2. Pydantic_Pratica.ipynb (Google Colab)
Aplicação prática voltada a área de saúde, na qual a precisão e a imutabilidade dos dados são críticas.
* **Validação de dados:** Criação de um modelo de triagem que impede falhas através de restrições biológicas (`ge`/`le` para temperatura e frequência cardíaca).
* **Imutabilidade e Segurança:** Aplicação de `frozen=True` para garantir que dados sensíveis (como CPF) não sejam alterados após o registro, e `SecretStr` para proteção de privacidade em logs.
* **Lógica de Atribuição:** Uso de `field_serializer` para padronização de saída de Enums clínicos.
* **Testes:** Bateria de testes de estresse que comprovam o bloqueio de e-mails malformatados, nomes inconsistentes e valores fora da realidade clínica.


## Tecnologias e Conceitos Explorados

* **Pydantic :** O motor central de validação (escrito em Rust para alta performance).
* **Type Hinting:** Uso extensivo das tipagens do Python para documentação e segurança em tempo de desenvolvimento.
* **FastAPI:** Utilizado como ferramenta de apoio para expor os modelos Pydantic via HTTP e simular o consumo de dados reais.
* **Poetry:** Gerenciamento de dependências e controle rigoroso do ambiente virtual (`pyproject.toml` e `poetry.lock`).

## Como Executar

### 1. Ambiente Local
1. Certifique-se de ter o Python 3.11+ instalado.
2. Instale as dependências necessárias:
   ```bash
   pip install pydantic[email] fastapi httpx
