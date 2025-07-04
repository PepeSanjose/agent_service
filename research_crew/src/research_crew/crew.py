from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool, WebsiteSearchTool, GithubSearchTool
from typing import List
import yaml
import os
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

class TechnicalDocCrew():
    """Tecnhical_Doc_Generation crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    def __init__(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_path, "config")
        with open(os.path.join(config_path, "agents_technical_doc.yaml"), "r", encoding="utf-8") as f:
            self.agents_config = yaml.safe_load(f)
        with open(os.path.join(config_path, "tasks_technical_doc.yaml"), "r", encoding="utf-8") as f:
            self.tasks_config = yaml.safe_load(f)
        self.agents = []
        self.tasks = []
        # Integración de GithubSearchTool para búsquedas en GitHub
        self.github_tool = GithubSearchTool(
            gh_token=os.environ.get("GITHUB_TOKEN", ""),
            content_types=['code', 'issue'],
            # github_repo='https://github.com/PepeSanjose/agent_service'  # ⚠️ Si el repo es privado, el token debe tener permisos de lectura. Si da error 422, deja esta línea comentada y usa búsquedas globales.
        )

    @agent
    def code_searcher(self) -> Agent:
        return Agent(
            config=self.agents_config['code_searcher'],
            tools=[self.github_tool],
            verbose=True
        )
    @agent
    def technical_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['technical_writer'], # type: ignore[index]
            verbose=True
        )

    @agent
    def doc_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config['doc_reviewer'], # type: ignore[index]
            verbose=True
        )
    
    @task
    def code_search_task(self) -> Task:
        return Task(
            config=self.tasks_config['code_search_task'],
        )

    @task
    def draft_doc_task(self) -> Task:
        return Task(
            config=self.tasks_config['draft_doc_task'], # type: ignore[index]
        )

    @task
    def review_doc_task(self) -> Task:
        return Task(
            config=self.tasks_config['review_doc_task'], # type: ignore[index]
            output_file='technical_doc.md'
        )


  

    def crew(self) -> Crew:
        """
        Crea el crew de generación de documentación técnica.
        Flujo:
        1. Revisa el código del repositorio siguiendo la indicación "haz un diseño técnico para añadir una funcionalidad".
        2. Redacta el diseño técnico propuesto.
        3. Revisa y mejora el diseño técnico generado.
        """
        # Instancia los agentes y tareas manualmente
        code_searcher = self.code_searcher()
        technical_writer = self.technical_writer()
        doc_reviewer = self.doc_reviewer()
        code_task = self.code_search_task()
        code_task.agent = code_searcher
        draft_task = self.draft_doc_task()
        draft_task.agent = technical_writer
        review_task = self.review_doc_task()
        review_task.agent = doc_reviewer
        return Crew(
            agents=[code_searcher, technical_writer, doc_reviewer],
            tasks=[code_task, draft_task, review_task],
            process=Process.sequential,
            verbose=True,
        )

@CrewBase
class ResearchCrew():
    """ResearchCrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            tools=[SerperDevTool(), WebsiteSearchTool()],
            verbose=True
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'], # type: ignore[index]
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'], # type: ignore[index]
            output_file='report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ResearchCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
