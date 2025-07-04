# ResearchCrew Crew

---

⚠️ **IMPORTANTE: No incluyas el campo `agent` como string en los archivos YAML de tareas (`tasks.yaml`, `tasks_technical_doc.yaml`, etc.)**

Si añades un campo `agent: nombre_agente` en el YAML de tareas, CrewAI intentará tratarlo como un objeto y lanzará errores como `'str' object has no attribute 'get'`.  
**La asignación de agentes a tareas debe hacerse manualmente en el código Python, no en el YAML.**  
Ejemplo correcto de tarea en YAML:
```yaml
mi_tarea:
  description: >
    Descripción de la tarea.
  expected_output: >
    Salida esperada.
```
Y en el código Python:
```python
tarea = Task(config=tasks_config['mi_tarea'])
tarea.agent = mi_agente
```
---

Welcome to the ResearchCrew Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/research_crew/config/agents.yaml` to define your agents
- Modify `src/research_crew/config/tasks.yaml` to define your tasks
- Modify `src/research_crew/crew.py` to add your own logic, tools and specific args
- Modify `src/research_crew/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the research_crew Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

---

## Despliegue de la API (FastAPI)

Para exponer la funcionalidad de ResearchCrew como un servicio web, sigue estos pasos:

1. **Activa tu entorno virtual** (si tienes uno):

- En Windows:
  ```bash
  .venv\Scripts\activate
  ```
- En Unix/Mac:
  ```bash
  source .venv/bin/activate
  ```

2. **Lanza el servidor FastAPI con Uvicorn** desde la raíz del proyecto:

```bash
uvicorn research_crew.api:app --reload --app-dir src
```

Esto expondrá la API en [http://localhost:8000](http://localhost:8000).  
Puedes acceder a la documentación interactiva (Swagger UI) en [http://localhost:8000/docs](http://localhost:8000/docs).

El endpoint principal es:

- `POST /run_crew`: Ejecuta el crew y devuelve el archivo `report.md` generado.

---
## Understanding Your Crew

The research_crew Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the ResearchCrew Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
