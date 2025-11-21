from crewai_tools import ScrapflyScrapeWebsiteTool
from os import getenv
from dotenv import load_dotenv
load_dotenv()

class WebScrapTool:
    """ Use esta ferramenta para fazer o scrape de {web} """
    def __init__(self):
        self.SCRAPFLY_API_KEY = getenv("SCRAPFLY_API_KEY")

    def _run(self):
        scrape_tool = ScrapflyScrapeWebsiteTool(api_key=self.SCRAPFLY_API_KEY)
        return  scrape_tool