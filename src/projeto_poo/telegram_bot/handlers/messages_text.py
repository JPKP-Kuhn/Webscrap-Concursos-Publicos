import json
from pathlib import Path
from ..user import User


# Class for leading with text
class MessagesText:
    DEFAULT_RESPONSE = f"Suporte para {0} não implementado ainda. Use /help para saber melhor como eu posso te ajudar."
    WRONG_RESPONSE = f"Preciso que você me informe os dados necessários para que possa te ajudar, use /help para saber mais."

    START_RESPONSE = f"Sou o bot que te ajuda a buscar por novos concursos públicos, do que você precisa? Digite /help para ver as opções disponíveis."

    HELP_RESPONSE = f"""
    - Primeiro, me informe qual a região, 'Norte', 'Sul', que você está buscando concursos, depois o seu estado, 'São Paulo', 'Rio de Janeiro', 'Minas Gerais', etc.\n
    - Também preciso saber qual a sua escolaridade, por exemplo, 'Ensino Fundamental', 'Ensino Médio', 'Ensino Superior', etc.
    """

    def __init__(self):
        """Inicializa a classe e carrega os padrões de resposta do JSON."""
        self.patterns = self._load_patterns()
        # Instância da classe User para gerenciar dados dos usuários (singleton)
        self.user = User()

    def _load_patterns(self) -> dict:
        """Carrega os padrões de resposta do arquivo JSON.

        Returns:
            Dicionário com os padrões carregados do JSON
        """
        json_path = Path(__file__).parent / "pattern_response.json"
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    def get_greeting(self, username: str | None = None) -> str:
        """Retorna a mensagem de saudação com o username do usuário.

        Args:
            username: Nome de usuário do Telegram (opcional)

        Returns:
            Mensagem de saudação formatada
        """
        if username:
            return f"Olá, {username}!"
        return "Olá!"


    def _find_estado(self, text_lower: str) -> tuple[str | None, str | None]:
        """Busca por estado no texto. Retorna (nome_estado, resposta).

        Args:
            text_lower: Texto normalizado em minúsculas

        Returns:
            Tupla (nome_estado, resposta) ou (None, None) se não encontrar
        """
        if "region" not in self.patterns:
            return None, None

        # Busca primeiro por estados (mais específico)
        for regiao_nome, regiao_data in self.patterns["region"].items():
            if "estados" in regiao_data:
                for estado_nome, estado_data in regiao_data["estados"].items():
                    if "estado" in estado_data:
                        estado_pattern = estado_data["estado"].lower()
                        if estado_pattern in text_lower:
                            return estado_data["estado"], estado_data.get("response")
        return None, None

    def _find_regiao(self, text_lower: str) -> tuple[str | None, str | None]:
        """Busca por região no texto. Retorna (nome_regiao, resposta).

        Args:
            text_lower: Texto normalizado em minúsculas

        Returns:
            Tupla (nome_regiao, resposta) ou (None, None) se não encontrar
        """
        if "region" not in self.patterns:
            return None, None

        for regiao_nome, regiao_data in self.patterns["region"].items():
            if "regiao" in regiao_data:
                regiao_pattern = regiao_data["regiao"].lower()
                if regiao_pattern in text_lower:
                    return regiao_data["regiao"], regiao_data.get("response")
        return None, None

    def _find_educacao(self, text_lower: str) -> tuple[str | None, str | None]:
        """Busca por nível de educação no texto. Retorna (nome_ensino, resposta).

        Args:
            text_lower: Texto normalizado em minúsculas

        Returns:
            Tupla (nome_ensino, resposta) ou (None, None) se não encontrar
        """
        if "education" not in self.patterns:
            return None, None

        for ensino_nome, ensino_data in self.patterns["education"].items():
            if "ensino" in ensino_data:
                ensino_pattern = ensino_data["ensino"].lower()
                if ensino_pattern in text_lower:
                    return ensino_data["ensino"], ensino_data.get("response")
        return None, None

    def get_text_response(self, text: str, user_id: int | None = None) -> str:
        """Retorna a resposta para o texto informado.
        Analisando se a resposta possui o padrão especificado.
        Busca primeiro por estado, depois região, e por fim educação.

        Args:
            text: Texto informado pelo usuário
            user_id: ID do usuário para rastreamento (opcional)

        Returns:
            Resposta para o texto informado
        """
        if not text:
            return self.DEFAULT_RESPONSE.format("texto vazio")

        # Normaliza o texto para busca (case-insensitive)
        text_lower = text.lower()

        # Inicializa dados do usuário se necessário
        if user_id is not None:
            user_data = self.user.get_user(user_id)
            if user_data is None:
                self.user.set_user(user_id)

        # Busca hierárquica: primeiro estados (mais específico), depois regiões, depois educação
        estado_nome, estado_response = self._find_estado(text_lower)
        regiao_nome, regiao_response = self._find_regiao(text_lower)
        ensino_nome, ensino_response = self._find_educacao(text_lower)

        # Atualiza dados do usuário usando a classe User
        if user_id is not None:
            regiao_para_atualizar = None
            if estado_nome:
                # Se encontrou estado, também atualiza a região correspondente
                if regiao_nome is None:
                    # Busca a região do estado
                    for regiao_key, regiao_data in self.patterns.get("region", {}).items():
                        if "estados" in regiao_data:
                            # Verifica se o estado está na lista de estados desta região
                            if estado_nome in regiao_data["estados"].keys():
                                regiao_para_atualizar = regiao_data.get("regiao")
                                break
                
                self.user.update_user_data(user_id, regiao=regiao_para_atualizar, estado=estado_nome)
            elif regiao_nome:
                self.user.update_user_data(user_id, regiao=regiao_nome)

            if ensino_nome:
                self.user.update_user_data(user_id, ensino=ensino_nome)

        # Monta a resposta baseada no que foi encontrado
        """
        responses = []

        # Prioriza estado sobre região
        if estado_response:
            responses.append(estado_response)
        elif regiao_response:
            responses.append(regiao_response)

        if ensino_response:
            responses.append(ensino_response)

        # Se encontrou algo, retorna a resposta combinada ou individual
        if responses:
            return " ".join(responses)
        """

        # Se não encontrou nada, verifica o que ainda falta
        if user_id is not None:
            user_info = self.user.get_user(user_id)
            if user_info:
                missing = []
                if not user_info.get("estado") and not user_info.get("regiao"):
                    missing.append("região/estado")
                if not user_info.get("ensino"):
                    missing.append("nível de formação")

                if missing:
                    return f"Entendi! Ainda preciso saber sua {', '.join(missing)}. Por favor, me informe."

        # Se nenhum padrão foi encontrado, retorna a resposta padrão
        return self.WRONG_RESPONSE.format(text)

