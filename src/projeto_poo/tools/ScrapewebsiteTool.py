from crewai_tools import ScrapeWebsiteTool

class ScrapewebsiteTool:
    """ 
    Use essa ferramenta para ajudar a realizar o scrape de websites.
    A URL do website será fornecida dinamicamente via inputs ({web}).
    """
    def __init__(self, web: str = None):
        """
        Inicializa a ferramenta de scrape.
        
        Args:
            web: URL base do website (opcional, pode ser fornecido dinamicamente)
        """
        self.web = web
        # Se não fornecer web na inicialização, cria uma tool genérica
        # que pode ser usada com URLs diferentes
        if web:
            self.tool = ScrapeWebsiteTool(website_url=web)
        else:
            # Cria uma tool sem URL específica - a URL será fornecida
            # dinamicamente quando o agente usar a tool
            self.tool = ScrapeWebsiteTool(website_url="www.pciconcursos.com.br/concursos/")

    def _run(self):
        """Retorna a tool do CrewAI"""
        return self.tool