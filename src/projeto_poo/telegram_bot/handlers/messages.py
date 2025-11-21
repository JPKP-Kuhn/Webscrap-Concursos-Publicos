from pyrogram.client import Client
from pyrogram import filters

# For basic messages
from .messages_text import MessagesText
from ..crewai_integration import CrewAIIntegration

__all__ = ["MessageHandler"]


class MessageHandler(MessagesText):
    """Classe responsável por receber as mensagens do telegram"""
    
    def __init__(self, client: Client):
        super().__init__()
        self.app = client
        # Inicializa a integração com o CrewAI usando a instância User compartilhada
        self.crewai_integration = CrewAIIntegration(self.user)
        self.setup_handlers()

    def setup_handlers(self) -> None:
        # Command handlers
        self.app.on_message(filters.command('start'))(self.handle_start)
        self.app.on_message(filters.command('help'))(self.handle_help)

        # Media handlers Não é usado
        self.app.on_message(filters.audio | filters.voice)(self.handle_audio)
        self.app.on_message(filters.photo)(self.handle_photo)
        self.app.on_message(filters.sticker)(self.handle_sticker)
        self.app.on_message(filters.video | filters.animation)(self.handle_video)

        # Text handlers
        self.app.on_message()(self.handle_text)
        self.app.on_message(filters.document)(self.handle_document)


    # Command handlers
    async def handle_start(self, client: Client, message):
        """Handle the start command."""
        username = message.from_user.username if message.from_user else None
        user_id = message.from_user.id if message.from_user else None
        
        # Armazena o usuário no estado global
        if user_id:
            self.user.set_user(user_id, username)
            print(f"Start called by {username} (ID: {user_id})")
        
        greeting = self.get_greeting(username)
        await message.reply(greeting)
        await message.reply(self.START_RESPONSE)


    async def handle_help(self, client: Client, message):
        """Handle the help command."""
        username = message.from_user.username if message.from_user else None
        print(f"Help called by {username}")
        await message.reply(self.HELP_RESPONSE)


    # Text handlers
    async def handle_text(self, client: Client, message):
        """Handle the text message."""
        if message.text:
            print(message.from_user.username, message.text)
            user_id = message.from_user.id if message.from_user else None
            
            if not user_id:
                await message.reply("Erro: não foi possível identificar o usuário. Use /start primeiro.")
                return
            
            # Garante que o usuário está no estado global
            if not self.user.get_user(user_id):
                username = message.from_user.username if message.from_user else None
                self.user.set_user(user_id, username)
            
            # Verifica se é uma confirmação
            text_lower = message.text.lower().strip()
            is_confirmation = text_lower in ["sim", "confirmar", "confirm", "yes", "ok", "vamos", "iniciar"]
            
            # Valida se tem todos os dados necessários
            is_valid, validation_message = self.crewai_integration.validate_user_data(user_id)
            
            # Se é confirmação e tem todos os dados, inicia o crewAI
            if is_confirmation and is_valid:
                self.user.mark_user_ready(user_id, True)
                await self.crewai_integration.execute_crew_ai(message, user_id)
                return
            
            # Se é confirmação mas não tem todos os dados
            if is_confirmation and not is_valid:
                await message.reply(
                    f"{validation_message}\n\n"
                    "Por favor, informe todas as informações necessárias antes de confirmar."
                )
                return
            
            # Processa a mensagem e atualiza os dados (não é confirmação)
            response = self.get_text_response(message.text, user_id)
            await message.reply(response)
            
            # Valida novamente após processar a mensagem
            is_valid, validation_message = self.crewai_integration.validate_user_data(user_id)
            
            if not is_valid:
                # Já enviou a resposta acima, só precisa informar o que falta
                return
            
            # Se chegou aqui, tem todos os dados. Pergunta se quer iniciar
            user_data = self.user.get_user(user_id)
            if user_data and not user_data.get("ready"):
                await message.reply(
                    f"\n✅ {validation_message}\n\n"
                    "Digite 'sim' ou 'confirmar' para iniciar a busca de concursos."
                )


    ########################## Handlers not Supported ##############################################
    async def handle_audio(self, client: Client, message):
        await message.reply(self.DEFAULT_RESPONSE.format("audio"))

    async def handle_photo(self, client: Client, message):
        await message.reply(self.DEFAULT_RESPONSE.format("photo"))

    async def handle_sticker(self, client: Client, message):
        await message.reply(self.DEFAULT_RESPONSE.format("sticker"))

    async def handle_video(self, client: Client, message):
        await message.reply(self.DEFAULT_RESPONSE.format("video"))
    
    async def handle_document(self, client: Client, message):
        await message.reply(self.DEFAULT_RESPONSE.format("documents"))

