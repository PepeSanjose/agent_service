from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from .crew import ResearchCrew
from pathlib import Path

app = FastAPI()

@app.post("/run_crew")
def run_crew():
    try:
        # Inicializa y ejecuta el crew
        crew_instance = ResearchCrew()
        crew = crew_instance.crew()
        crew.kickoff()  # Ejecuta el crew

        # Devuelve el archivo de reporte generado de forma robusta usando pathlib
        report_path = Path(__file__).resolve().parent.parent.parent / "report.md"
        if report_path.exists():
            return FileResponse(str(report_path), media_type="text/markdown", filename="report.md")
        else:
            return JSONResponse(content={"error": "No se encontró el reporte"}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
