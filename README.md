# ProjetoPoo Crew

Projeto de POO1, UFSC\
Chatbot Telegram usando pyrogram e tgcrypt\
Webscraping usando agentes de IA, com crewAI

## Instalação

Certifique-se de que você possui Python \>=3.10 \<3.14 instalado no
sistema.\
Este projeto utiliza [**UV**](https://docs.astral.sh/uv/) para gerenciar dependências e lidar com
pacotes, oferecendo uma experiência de configuração e execução simples.

Primeiro, caso ainda não tenha, instale o `uv`:

Em seguida, navegue até o diretório do seu projeto e instale as
dependências:

(Opcional) Trave as dependências e instale-as usando o comando da CLI:
Para poder instalar todas as dependências
```bash
uv sync
```

### Personalização

**Adicione sua `OPENAI_API_KEY` no arquivo `.env`**

-   Modifique `src/projeto_poo/config/agents.yaml` para definir seus
    agentes\
-   Modifique `src/projeto_poo/config/tasks.yaml` para definir suas
    tarefas\
-   Modifique `src/projeto_poo/crew.py` para adicionar sua própria
    lógica, ferramentas e argumentos específicos\
-   Modifique `src/projeto_poo/main.py` para adicionar entradas
    personalizadas para seus agentes e tarefas

## Executando o Projeto

Para iniciar sua equipe de agentes de IA e começar a execução das
tarefas, execute o seguinte a partir da pasta raiz do projeto:

```bash
crewai run
```

Este comando inicializa o Projeto-Poo Crew, montando os agentes e
atribuindo tarefas conforme definido na configuração.

Este exemplo, sem modificações, criará um arquivo `report.md` na pasta
raiz com o resultado de uma pesquisa sobre LLMs.

## Entendendo Sua Crew

O projeto possui 5 agents-
1. Planejador de contexto
2. Webscrap
3. Analisador de Dados
4. Resumir texto
5. Análise Final
