from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .crew import ResearchCrew, TechnicalDocCrew
from pathlib import Path

app = FastAPI()

# Habilitar CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Cambia esto si tu frontend está en otro origen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get_crew")
def get_crew(crew_name: str = "research"):
    try:
        if crew_name == "technical_doc":
            crew_instance = TechnicalDocCrew()
        else:
            crew_instance = ResearchCrew()
        crew = crew_instance.crew()

        # Obtener agentes y tareas desde el objeto Crew
        print("DEBUG crew.agents:", getattr(crew, "agents", []))
        print("DEBUG crew.tasks:", getattr(crew, "tasks", []))
        # Leer el YAML de configuración de agentes directamente para poblar el array agents
        import yaml, os
        base_path = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_path, "config")
        if crew_name == "technical_doc":
            agents_yaml_path = os.path.join(config_path, "agents_technical_doc.yaml")
        else:
            agents_yaml_path = os.path.join(config_path, "agents.yaml")
        with open(agents_yaml_path, "r", encoding="utf-8") as f:
            agents_config = yaml.safe_load(f)
        agents = []
        for key, agent_cfg in agents_config.items():
            agents.append({
                "id": agent_cfg.get("name", key),
                "role": agent_cfg.get("role", ""),
                "goal": agent_cfg.get("goal", ""),
                "backstory": agent_cfg.get("backstory", "")
            })
        tasks = []
        for task in getattr(crew, "tasks", []):
            agent_obj = getattr(task, "agent", "")
            # Serializar el agente como objeto con name y role
            try:
                agent_name = ""
                agent_role = ""
                if hasattr(agent_obj, "config") and isinstance(agent_obj.config, dict):
                    agent_name = agent_obj.config.get("name", "")
                if not agent_name and hasattr(agent_obj, "name"):
                    agent_name = getattr(agent_obj, "name", str(agent_obj))
                if hasattr(agent_obj, "role"):
                    agent_role = getattr(agent_obj, "role", "")
                agent_serialized = {"name": agent_name, "role": agent_role}
            except Exception as e:
                print("DEBUG error accediendo a agent_obj:", agent_obj, e)
                agent_serialized = {"name": str(agent_obj), "role": ""}
            tasks.append({
                "id": getattr(task, "name", ""),
                "description": getattr(task, "description", ""),
                "agent": agent_serialized
            })
        # Relaciones simples: cada tarea depende de la anterior (secuencial)
        edges = []
        for i in range(1, len(tasks)):
            edges.append({
                "source": tasks[i-1]["id"],
                "target": tasks[i]["id"]
            })
        print("DEBUG agents:", agents)
        print("DEBUG tasks:", tasks)
        return JSONResponse(content={
            "agents": agents,
            "tasks": tasks,
            "edges": edges
        })
    except Exception as e:
        print("ERROR en /get_crew:", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)

from fastapi import Request

@app.post("/run_crew")
async def run_crew(request: Request):
    try:
        data = await request.json()
        topic = data.get("topic")
        crew_name = data.get("crew_name", "research")
        if not topic or not str(topic).strip():
            return JSONResponse(content={"error": "El campo 'topic' es obligatorio y no puede estar vacío."}, status_code=400)
        # Inicializa y ejecuta el crew con el topic recibido
        if crew_name == "technical_doc":
            crew_instance = TechnicalDocCrew()
            output_file = "technical_doc.md"
        else:
            crew_instance = ResearchCrew()
            output_file = "report.md"
        crew = crew_instance.crew()
        from datetime import datetime
        inputs = {
            "topic": topic.strip(),
            "current_year": str(datetime.now().year)
        }
        crew.kickoff(inputs=inputs)  # Ejecuta el crew con el topic y el año actual

        # Devuelve el archivo de reporte generado de forma robusta usando pathlib
        report_path = Path(__file__).resolve().parent.parent.parent / output_file
        if report_path.exists():
            return FileResponse(str(report_path), media_type="text/markdown", filename=output_file)
        else:
            return JSONResponse(content={"error": "No se encontró el reporte"}, status_code=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)
