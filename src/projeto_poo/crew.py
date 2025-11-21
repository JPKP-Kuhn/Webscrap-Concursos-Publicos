from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

from .tools import ScrapflyTool as SF
from .tools import ScrapewebsiteTool as SW

# Instancia a ferramenta de webscraping
# ScrapflyTool não precisa de parâmetros (usa API key de variável de ambiente)
scrapefly_tool = SF.WebScrapTool()._run()

# ScrapeWebsiteTool pode ser criada sem URL específica inicialmente
# A URL será fornecida dinamicamente via inputs {web} quando o agente executar
scrape_tool = SW.ScrapewebsiteTool()._run()


@CrewBase
class ProjetoPoo():
    """ProjetoPoo crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def context_planner_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['context_planner_agent'], # type: ignore[index]
            verbose=True,
            allow_delegation=False,
            memory=True,
            reasoning=True,
            tools=[],
            allow_code_executer=False,
            multimodal=False
        )

    @agent
    def webscrap_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['webscrap_agent'], # type: ignore[index]
            verbose=True,
            tools=[scrapefly_tool, scrape_tool],
            memory=False,
            allow_delegation=False,
            reasoning=False,
            allow_code_execution=False
        )

    @agent
    def data_analysis_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['data_analysis_agent'], # type: ignore[index]
            verbose=True,
            allow_delegation=False,
            memory=True,
            reasoning=True,
            tools=[],
            allow_code_execution=False,
            multimodal=False
        )

    @agent
    def content_resume_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['content_resume_agent'], # type: ignore[index]
            verbose=True,
            allow_delegation=False,
            memory=True,
            reasoning=True,
            tools=[],
            allow_code_execution=False,
            multimodal=False
        )

    @agent
    def final_report_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['final_report_agent'], # type: ignore[index]
            verbose=True,
            allow_delegation=False,
            memory=True,
            reasoning=True,
            tools=[],
            allow_code_execution=False,
            multimodal=False
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def content_planner_task(self) -> Task:
        return Task(
            config=self.tasks_config['context_planner_text'], # type: ignore[index]
        )

    @task
    def webscrap_task(self) -> Task:
        return Task(
            config=self.tasks_config['webscrap_task'], # type: ignore[index]
            output_file='report.md'
        )

    @task
    def data_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['data_analysis_task'], # type: ignore[index]
            output_file='analysis.md'
        )

    @task
    def content_resume_task(self) -> Task:
        return Task(
            config=self.tasks_config['content_resume_task'], # type: ignore[index]
            output_file='summary.md'
        )

    @task
    def final_report_task(self) -> Task:
        return Task(
            config=self.tasks_config['final_report_task'], # type: ignore[index]
            output_file='final_report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the WebscrapConcursos crew"""

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            memory=True
        )

