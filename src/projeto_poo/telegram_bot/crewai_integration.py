"""
Módulo responsável pela integração entre o Telegram Bot e o CrewAI.
Centraliza toda a lógica de preparação e execução do crewAI.
"""
import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from pyrogram.types import Message
from projeto_poo.crew import ProjetoPoo
from .user import User

# Thread pool executor para executar o crewAI de forma assíncrona
executor = ThreadPoolExecutor(max_workers=3)


class CrewAIIntegration:
    """Classe responsável por gerenciar a integração com o CrewAI."""
    
    # URL base para webscraping
    BASE_URL = "https://www.pciconcursos.com.br"
    
    def __init__(self, user: User):
        """
        Inicializa a integração com o CrewAI.
        
        Args:
            user: Instância da classe User (singleton)
        """
        self.user = user
    
    def validate_user_data(self, user_id: int) -> tuple[bool, str]:
        """
        Valida se o usuário tem todos os dados necessários para executar o crewAI.
        
        Args:
            user_id: ID do usuário do Telegram
            
        Returns:
            Tupla (is_valid, message) onde is_valid é True se todos os dados estão presentes
        """
        is_ready = self.user.is_user_ready(user_id)
        if is_ready:
            user_data = self.user.get_user(user_id)
            parts = []
            if user_data.get("estado"):
                parts.append(f"Estado: {user_data['estado']}")
            elif user_data.get("regiao"):
                parts.append(f"Região: {user_data['regiao']}")
            if user_data.get("ensino"):
                parts.append(f"Escolaridade: {user_data['ensino']}")
            
            message = "Informações coletadas: " + ", ".join(parts)
            return True, message
        else:
            user_data = self.user.get_user(user_id)
            if not user_data:
                return False, "Por favor, use /start primeiro."
            
            missing = []
            if not user_data.get("estado") and not user_data.get("regiao"):
                missing.append("região ou estado")
            if not user_data.get("ensino"):
                missing.append("nível de escolaridade")
            
            message = f"Ainda preciso saber sua {', '.join(missing)}."
            return False, message
    
    def get_topic_for_crew(self, user_id: int) -> str:
        """
        Constrói o tópico para o crewAI baseado nos dados do usuário.
        
        Args:
            user_id: ID do usuário do Telegram
            
        Returns:
            String formatada com o tópico contendo todas as informações do usuário
        """
        return self.user.build_topic(user_id)
    
    def prepare_inputs(self, user_id: int, topic: Optional[str] = None, 
                      base_url: Optional[str] = None) -> dict:
        """
        Prepara os inputs necessários para executar o crewAI.
        
        Args:
            user_id: ID do usuário do Telegram
            topic: Tópico formatado (opcional, será construído se não fornecido)
            base_url: URL base para webscraping (opcional, usa padrão se não fornecido)
            
        Returns:
            Dicionário com os inputs formatados para o crewAI
            
        Raises:
            ValueError: Se o usuário não for encontrado ou user_data não for um dicionário
        """
        user_data = self.user.get_user(user_id)
        if not user_data:
            raise ValueError(f"Usuário {user_id} não encontrado.")
        
        # Valida que user_data é um dicionário
        if not isinstance(user_data, dict):
            raise ValueError(
                f"user_data deve ser um dicionário, mas recebeu: {type(user_data)}. "
                f"Valor: {user_data}"
            )
        
        if not topic:
            topic = self.get_topic_for_crew(user_id)
        
        if not base_url:
            base_url = self.BASE_URL
        
        # Garante que 'user' seja uma string
        user_name = user_data.get("user") if isinstance(user_data, dict) else f"user_{user_id}"
        if not user_name:
            user_name = f"user_{user_id}"
        
        inputs = {
            'topic': str(topic) if topic else "",
            'user': str(user_name),
            'web': str(base_url),
            'current_year': str(datetime.now().year)
        }
        
        # Valida que todos os valores são strings (como esperado pelo crewAI)
        for key, value in inputs.items():
            if not isinstance(value, str):
                print(f"[AVISO] Input '{key}' não é string: {type(value)} = {value}")
                inputs[key] = str(value)
        
        return inputs
    
    def _run_crew_ai(self, inputs: dict):
        """
        Executa o crewAI de forma síncrona (chamado em thread separada).
        
        Args:
            inputs: Dicionário com os inputs para o crewAI
            
        Returns:
            Resultado do crewAI
            
        Raises:
            Exception: Se ocorrer um erro durante a execução
        """
        import traceback
        
        try:
            # Valida os inputs antes de passar para o crewAI
            if not isinstance(inputs, dict):
                raise ValueError(f"Inputs deve ser um dicionário, mas recebeu: {type(inputs)}")
            
            # Verifica se todos os valores esperados estão presentes
            print(f"[DEBUG] Executando crewAI com inputs: {inputs}")
            print(f"[DEBUG] Tipo dos inputs: {type(inputs)}")
            print(f"[DEBUG] Tipo dos valores em inputs:")
            for key, value in inputs.items():
                print(f"  - {key}: {type(value).__name__} = {value}")
            
            crew = ProjetoPoo().crew()
            result = crew.kickoff(inputs=inputs)
            
            # Verifica o tipo do resultado
            print(f"[DEBUG] Resultado do crewAI - Tipo: {type(result)}")
            if hasattr(result, '__class__'):
                print(f"[DEBUG] Classe do resultado: {result.__class__.__name__}")
            
            return result
        except AttributeError as e:
            error_info = {
                "erro": str(e),
                "tipo": type(e).__name__,
                "mensagem": f"'str' object has no attribute 'get'",
                "traceback": traceback.format_exc()
            }
            print(f"[ERRO DETALHADO] AttributeError: {error_info}")
            raise Exception(f"Erro de atributo no crewAI: {str(e)}\n\nTraceback completo:\n{traceback.format_exc()}")
        except Exception as e:
            error_info = {
                "erro": str(e),
                "tipo": type(e).__name__,
                "traceback": traceback.format_exc()
            }
            print(f"[ERRO DETALHADO] Exception: {error_info}")
            print(f"[ERRO COMPLETO] Traceback:\n{traceback.format_exc()}")
            raise
    
    async def execute_crew_ai(self, message: Message, user_id: int) -> None:
        """
        Executa o crewAI de forma assíncrona e envia o resultado para o usuário.
        
        Args:
            message: Mensagem do Telegram para enviar respostas
            user_id: ID do usuário do Telegram
        """
        # Valida se o usuário existe
        user_data = self.user.get_user(user_id)
        if not user_data:
            await message.reply("Erro: dados do usuário não encontrados.")
            return
        
        # Constrói o tópico
        topic = self.get_topic_for_crew(user_id)
        if not topic:
            await message.reply("Erro: não foi possível construir o tópico.")
            return
        
        # Prepara os inputs
        try:
            inputs = self.prepare_inputs(user_id, topic=topic)
        except ValueError as e:
            await message.reply(f"Erro: {str(e)}")
            return
        
        # Notifica o usuário que o processo foi iniciado
        await message.reply("Iniciando processo de busca... Isso pode levar alguns minutos.")
        
        # Executa o crewAI em uma thread separada para não bloquear o event loop
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                executor,
                self._run_crew_ai,
                inputs
            )
            
            # Formata e envia o resultado para o usuário
            result_str = str(result) if result else "Busca concluída, mas nenhum resultado foi retornado."
            
            # Limita o tamanho da mensagem (Telegram tem limite de 4096 caracteres)
            if len(result_str) > 4000:
                result_str = result_str[:4000] + "\n\n... (resultado truncado)"
            
            await message.reply(f"✅ Busca concluída!\n\n{result_str}")
            
        except Exception as e:
            import traceback
            
            # Captura informações detalhadas do erro
            error_type = type(e).__name__
            error_message = str(e)
            full_traceback = traceback.format_exc()
            
            # Log detalhado no console
            print(f"\n{'='*60}")
            print(f"[ERRO CAPTURADO]")
            print(f"Tipo: {error_type}")
            print(f"Mensagem: {error_message}")
            print(f"\nTraceback completo:")
            print(full_traceback)
            print(f"{'='*60}\n")
            
            # Envia mensagem mais informativa ao usuário
            # (mas sem o traceback completo para não assustar)
            user_friendly_msg = f"❌ Erro ao executar a busca:\n\n"
            user_friendly_msg += f"Tipo: {error_type}\n"
            user_friendly_msg += f"Detalhes: {error_message[:500]}"  # Limita tamanho
            
            await message.reply(user_friendly_msg)

