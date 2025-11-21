"""
Módulo para gerenciar variáveis globais do bot do Telegram.
Armazena informações dos usuários e estado do bot.
"""

# Variáveis globais para armazenar informações dos usuários
# Formato: {user_id: {"user": username, "regiao": str, "estado": str, "ensino": str, "ready": bool}}
class User:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Implementa o padrão Singleton para garantir uma única instância."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__user_global_state = {}
            cls._initialized = True
        return cls._instance
    
    def __init__(self):
        """Inicializa a instância singleton apenas uma vez."""
        # O estado é inicializado no __new__ para garantir que só aconteça uma vez
        pass

    def set_user(self, user_id: int, username: str | None = None):
        """
        Define o usuário no estado global.
        
        Args:
            user_id: ID do usuário do Telegram
            username: Nome de usuário (opcional)
        """
        if user_id not in self.__user_global_state:
            self.__user_global_state[user_id] = {
                "user": username or f"user_{user_id}",
                "regiao": None,
                "estado": None,
                "ensino": None,
                "ready": False
            }
        else:
            if username:
                self.__user_global_state[user_id]["user"] = username

    def update_user_data(self, user_id: int, regiao: str | None = None, 
                        estado: str | None = None, ensino: str | None = None):
        """
        Atualiza os dados do usuário no estado global.
        
        Args:
            user_id: ID do usuário do Telegram
            regiao: Região do usuário (opcional)
            estado: Estado do usuário (opcional)
            ensino: Nível de ensino do usuário (opcional)
        """
        if user_id not in self.__user_global_state:
            self.set_user(user_id)
        
        if regiao:
            self.__user_global_state[user_id]["regiao"] = regiao
        if estado:
            self.__user_global_state[user_id]["estado"] = estado
        if ensino:
            self.__user_global_state[user_id]["ensino"] = ensino


    def get_user(self, user_id: int) -> dict | None:
        """
        Retorna os dados do usuário.
        
        Args:
            user_id: ID do usuário do Telegram
            
        Returns:
            Dicionário com os dados do usuário ou None se não existir
        """
        return self.__user_global_state.get(user_id)


    def is_user_ready(self,user_id: int) -> bool:
        """
        Verifica se o usuário tem todas as informações necessárias.
        
        Args:
            user_id: ID do usuário do Telegram
            
        Returns:
            True se o usuário tem todas as informações necessárias, False caso contrário
        """
        if user_id not in self.__user_global_state:
            return False
        
        user_data = self.__user_global_state[user_id]
        # Precisa ter pelo menos região OU estado, e ensino
        has_location = user_data.get("estado") or user_data.get("regiao")
        has_education = user_data.get("ensino")
        
        return bool(has_location and has_education)


    def build_topic(self, user_id: int) -> str:
        """
        Constrói o tópico descritivo a partir dos dados do usuário para o crewAI.
        Gera um texto natural e detalhado que descreve as preferências do usuário.
        
        Args:
            user_id: ID do usuário do Telegram
            
        Returns:
            String formatada com o tópico descritivo contendo todas as informações do usuário
        """
        if user_id not in self.__user_global_state:
            return ""
        
        user_data = self.__user_global_state[user_id]
        
        # Constrói uma descrição natural e descritiva similar ao exemplo fornecido
        topic_lines = []
        
        # Parte da localização - formato mais descritivo
        if user_data.get("estado"):
            estado = user_data['estado']
            if user_data.get("regiao"):
                regiao = user_data['regiao']
                topic_lines.append(f"Sou da região {regiao}, moro no estado de {estado}")
            else:
                topic_lines.append(f"Moro no estado de {estado}")
            topic_lines.append("e estou procurando por concursos públicos")
        elif user_data.get("regiao"):
            regiao = user_data['regiao']
            topic_lines.append(f"Sou da região {regiao} e estou procurando por concursos públicos")
        
        # Parte da escolaridade
        if user_data.get("ensino"):
            ensino = user_data['ensino']
            topic_lines.append(f"com vagas para nível {ensino.lower()}.")
        else:
            topic_lines.append(".")
        
        # Adiciona informações complementares para melhorar a busca
        topic_lines.append(
            "Gostaria de encontrar concursos que ofereçam uma boa faixa salarial, "
            "de preferência acima de R$ 3.000,00, e que tenham inscrições abertas ou "
            "com datas de provas próximas. Além disso, seria ótimo se os concursos "
            "fossem para órgãos reconhecidos e com boa reputação."
        )
        
        # Junta tudo em um texto descritivo com quebras de linha
        topic = " ".join(topic_lines) if topic_lines else ""
        
        return topic


    def mark_user_ready(self, user_id: int, ready: bool = True):
        """
        Marca o usuário como pronto para iniciar o crewAI.
        
        Args:
            user_id: ID do usuário do Telegram
            ready: Se o usuário está pronto (padrão: True)
        """
        if user_id in self.__user_global_state:
            self.__user_global_state[user_id]["ready"] = ready

