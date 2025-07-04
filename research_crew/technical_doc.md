# agent_service - Documentación Técnica

Repositorio: [PepeSanjose/agent_service](https://github.com/PepeSanjose/agent_service)

---

## Índice

1. [Visión General](#visión-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Flujo de Trabajo y Componentes](#flujo-de-trabajo-y-componentes)
5. [Ejemplo de Uso: Endpoints y Casos de Uso](#ejemplo-de-uso-endpoints-y-casos-de-uso)
6. [Guía de Configuración y Ejecución](#guía-de-configuración-y-ejecución)
7. [Pruebas y Calidad](#pruebas-y-calidad)
8. [Referencias y Recursos](#referencias-y-recursos)
9. [Consideraciones Finales y Recomendaciones](#consideraciones-finales-y-recomendaciones)

---

## Visión General

**agent_service** es un backend modular desarrollado en Python utilizando FastAPI. Está diseñado siguiendo principios de arquitectura limpia y separación de responsabilidades, soportando la gestión, orquestación y ciclo de vida de agentes inteligentes o automatizados. Este servicio facilita la escalabilidad, el mantenimiento y las pruebas, promoviendo buenas prácticas como desacoplamiento, tipado estático, documentación automática de APIs, y abstracción del acceso a datos.

### Objetivos principales

- Exponer una API HTTP RESTful robusta, segura y autodocumentada.
- Separar la lógica de negocio (Service Layer) del acceso a datos (Repository Layer).
- Permitirse la integración y ciclo de vida de múltiples agentes, facilitando la orquestación.
- Mejorar la extensibilidad y la capacidad de prueba de cada componente del sistema.
- Aplicar patrones y estructuras de código validadas en la industria y la comunidad Python.

---

## Arquitectura del Sistema

La arquitectura propuesta para **agent_service** es multicapa, inspirada en Clean Architecture y buenas prácticas de sistemas desacoplados:

- **Entrypoint/API Layer:** Expone la API utilizando FastAPI. Valida y serializa peticiones y respuestas mediante Pydantic (esquemas).
- **Service/Agent Layer:** Implementa la lógica de negocio y la gestión integral de los agentes. Orquesta las operaciones complejas de dominio.
- **Repository Layer:** Abstrae la persistencia y recuperación de datos, facilitando el cambio de tecnologías de almacenamiento o la integración con fuentes externas.
- **Modelos:** Define contratos de datos entre capas (DTOs, Pydantic Schemas, entidades de dominio).
- **Core/Configuración:** Utilidades, configuración de parámetros globales y seguridad del sistema.

---

## Estructura del Proyecto

```plaintext
agent_service/
├── app/
│   ├── main.py             # FastAPI entrypoint
│   ├── api/                # Routers y endpoints
│   ├── core/               # Configuración, utilidades globales, seguridad
│   ├── services/           # Lógica de negocio y agentes
│   ├── models/             # Esquemas Pydantic, DTOs, entidades
│   ├── repositories/       # Acceso a fuentes de datos
├── agent/                  # Implementaciones específicas de agentes (si aplica)
├── tests/                  # Pruebas unitarias e integración
├── requirements.txt        # Dependencias
├── README.md
```

#### Diagrama de Componentes (descripción textual)

1. **main.py** inicia la aplicación FastAPI y monta los routers definidos en `app/api/`.
2. **API Layer (api/):** Encapsula rutas, validación de datos, y delega llamadas a la capa de servicios.
3. **Service/Agent Layer (services/ y agent/):** Contiene la lógica de dominio y el ciclo de vida de los agentes, separada del framework.
4. **Repository Layer (repositories/):** Gestiona el acceso y la persistencia de datos.
5. **tests/** incluye pruebas unitarias y de integración asegurando la calidad del sistema.

---

## Flujo de Trabajo y Componentes

1. **Recepción de Solicitudes:** El usuario/cliente realiza una petición HTTP (por ejemplo, crear agente, consultar estado, ejecutar tarea).
2. **Validación y Routing:** FastAPI valida el payload a través de modelos Pydantic y enruta al endpoint adecuado.
3. **Orquestación de Negocio:** El endpoint invoca la función/lógica pertinente en la capa de servicios/agentes.
4. **Interacción con Datos:** Los servicios interactúan con repositorios para consultar o persistir información.
5. **Respuesta:** El resultado se serializa y retorna siguiendo el contrato (schema) esperado.

---

## Ejemplo de Uso: Endpoints y Casos de Uso

A continuación, se muestra una implementación referencial del flujo típico (crear y consultar agentes):

### 1. Definición de Endpoints

```python
# app/api/agents.py
from fastapi import APIRouter, HTTPException
from app.schemas import AgentCreate, AgentRead
from app.services.agent_service import create_agent, get_agent

router = APIRouter(prefix="/agents", tags=["Agents"])

@router.post("/", response_model=AgentRead, status_code=201)
def api_create_agent(agent: AgentCreate):
    agent_obj = create_agent(agent)
    if not agent_obj:
        raise HTTPException(status_code=400, detail="Agent could not be created")
    return agent_obj

@router.get("/{agent_id}", response_model=AgentRead)
def api_get_agent(agent_id: int):
    agent_obj = get_agent(agent_id)
    if not agent_obj:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_obj
```

### 2. Servicio de Agentes

```python
# app/services/agent_service.py
from app.models import Agent
from app.repositories.agent_repository import AgentRepository

def create_agent(agent_data):
    agent = Agent(**agent_data.dict())
    return AgentRepository.save(agent)

def get_agent(agent_id):
    return AgentRepository.get(agent_id)
```

### 3. Repositorio de Agentes

```python
# app/repositories/agent_repository.py
class AgentRepository:
    _db = {}

    @classmethod
    def save(cls, agent):
        agent.id = len(cls._db) + 1
        cls._db[agent.id] = agent
        return agent

    @classmethod
    def get(cls, agent_id):
        return cls._db.get(agent_id)
```

### 4. Modelos y Esquemas

```python
# app/schemas.py
from pydantic import BaseModel

class AgentCreate(BaseModel):
    name: str
    type: str

class AgentRead(BaseModel):
    id: int
    name: str
    type: str
    status: str
```

```python
# app/models.py
from pydantic import BaseModel

class Agent(BaseModel):
    id: int = None
    name: str
    type: str
    status: str = 'inactive'
```

### 5. Ejemplo de Request HTTP (curl):

```bash
curl -X POST http://localhost:8000/agents/ -H "Content-Type: application/json" -d '{"name":"Agent1", "type":"bot"}'
```

---

## Guía de Configuración y Ejecución

1. **Requisitos previos:**  
   - Python 3.9 o superior  
   - pip

2. **Instalación de dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecución del servidor:**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Acceso a la documentación automática de la API:**  
   [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)

5. **Variables de entorno:**  
   - Definir configuración en `app/core/config.py` o mediante variables de entorno para parámetros como la conexión a BD, claves, etc.

---

## Pruebas y Calidad

- **Tests unitarios y de integración:**  
  Se recomienda mantener tests independientes para cada capa (`tests/`).  
  Utiliza `pytest` y `httpx` para tests de endpoints.

- **Cobertura de código:**  
  Contrastar la cobertura ejecutando:
  ```bash
  pytest --cov app/
  ```

- **Integración continua (CI):**  
  Configura un workflow de GitHub Actions o similar.

- **Buenas prácticas adicionales:**  
  - Añade linting automático (pylint/ruff/flake8).
  - Usa pre-commit hooks para calidad de código.
  - Asegura type checking con mypy.

---

## Referencias y Recursos

- [Full Stack FastAPI PostgreSQL (cookiecutter)](https://github.com/tiangolo/full-stack-fastapi-postgresql)
- [FastAPI Clean Architecture Example](https://github.com/edudepetris/fastapi-clean-architecture)
- [FastAPI Microservices Template](https://github.com/nsidnev/fastapi-template)
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- [Jina-AI (framework de microservicios para agentes)](https://github.com/jina-ai/jina)
- [AgentPy (modelado y simulación de agentes)](https://github.com/AutonomyLab/agentpy)
- [FastAPI + SQLAlchemy Example](https://github.com/miguelgrinberg/fastapi-sqlalchemy)
- [httpx (peticiones HTTP asíncronas)](https://github.com/encode/httpx)

---

## Consideraciones Finales y Recomendaciones

- **Separación de capas:** Mantén la arquitectura modular para facilitar la escalabilidad, mantenibilidad y pruebas.
- **Evolución del dominio:** Refina los nombres y estructuras a medida que definan claramente los casos de uso de agentes y su ciclo de vida.
- **Seguridad:** Implementa autenticación/autorización (ej. OAuth2 o JWT) en la capa API.
- **Manejo robusto de errores:** Mejora la gestión y el logging de errores en todas las capas.
- **Documentación continua:** Mantén la documentación en línea con los cambios, documenta claramente los endpoints y agrega ejemplos de requests/responses.
- **Extensibilidad:** Si tu dominio lo requiere, evalúa la integración con frameworks de agentes externos o sistemas distribuidos.

---

> **Este documento ha sido revisado y mejorado atendiendo a criterios de claridad, estructura, mejores prácticas y recomendaciones para publicación e implementación profesional. Se recomienda actualizar tras cada iteración funcional significativa.**