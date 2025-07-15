# Calendar API

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Modern-green?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker)

API RESTful para gerenciar eventos e agendamentos em qualquer servidor de calendário compatível com o padrão **CalDAV**. Construída com FastAPI, esta API oferece uma interface moderna e fácil de usar para interagir com seus calendários.

## Funcionalidades

- **Gerenciamento de Agendamentos:** Crie, leia, atualize e delete eventos no calendário.
- **Consulta de Disponibilidade:** Verifique horários livres em um determinado dia para evitar conflitos.
- **Filtro por Período:** Liste agendamentos filtrando por um intervalo de datas.
- **Prevenção de Conflitos:** A API impede a criação de eventos em horários já ocupados.
- **Compatibilidade Universal:** Funciona com qualquer servidor CalDAV (ex: Nextcloud, Google Calendar, etc.).

## Arquitetura

O projeto segue uma **Arquitetura em Camadas** para garantir a separação de responsabilidades, testabilidade e manutenibilidade:

-   **`main.py`**: Ponto de entrada da aplicação. Inicializa o FastAPI e carrega os módulos da API.
-   **`src/api`**: Camada de API (*Controllers*). Define os endpoints, recebe as requisições HTTP e retorna as respostas.
-   **`src/services`**: Camada de Serviço (*Use Cases*). Contém a lógica de negócio principal da aplicação.
-   **`src/clients`**: Camada de Clientes (*Repositories*). Responsável pela comunicação com o servidor CalDAV.
-   **`src/models`**: Camada de Modelos (*Schemas*). Define os modelos de dados e validação com Pydantic.

## Como Começar

Você pode executar o projeto de duas maneiras: usando Docker (recomendado para facilidade) ou localmente em um ambiente Python.

### Pré-requisitos

- Git
- Docker e Docker Compose (para a opção com container)
- Python 3.10+ (para a opção de execução local)

### 1. Usando Docker (Recomendado)

Esta é a maneira mais simples de subir a API.

1.  **Clone o repositório:**
    ```bash
    git clone <https://github.com/euoguss/SimpleCalDav>
    cd CalendarApi
    ```

2.  **Configure as variáveis de ambiente:**
    Copie o arquivo de exemplo `.env.example` para um novo arquivo chamado `.env` e preencha com suas credenciais do servidor CalDAV.
    ```bash
    cp .env.example .env
    ```

3.  **Suba o container com Docker Compose:**
    Este comando irá construir a imagem e iniciar o container.
    ```bash
    docker-compose up
    ```

Pronto! A API estará disponível em [http://localhost:8000](http://localhost:8000). Você pode acessar a documentação interativa em [http://localhost:8000/docs](http://localhost:8000/docs).

### 2. Executando Localmente

Use esta opção para desenvolvimento ou se preferir não usar Docker.

1.  **Clone e acesse o repositório** (como no passo 1 do Docker).

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    # No Windows: .\venv\Scripts\activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente** (como no passo 2 do Docker).

5.  **Inicie o servidor:**
    ```bash
    python main.py
    ```

A API estará disponível em [http://localhost:8000/docs](http://localhost:8000/docs).

## Endpoints da API

A documentação completa e interativa de todos os endpoints está disponível na interface do Swagger em `/docs` quando a API está em execução.

- `GET /api/v1/appointments/free_slots/`: Lista horários disponíveis.
- `POST /api/v1/appointments/`: Cria um novo agendamento.
- `GET /api/v1/appointments/`: Lista todos os agendamentos (com filtros de data).
- `GET /api/v1/appointments/{id}`: Obtém um agendamento específico.
- `PUT /api/v1/appointments/{id}`: Atualiza um agendamento.
- `DELETE /api/v1/appointments/{id}`: Deleta um agendamento.

## Contribuições

Contribuições são muito bem-vindas! Sinta-se à vontade para abrir uma **issue** para relatar um bug ou sugerir uma melhoria, ou enviar um **pull request** com suas alterações.
