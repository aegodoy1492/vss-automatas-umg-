# VSS · Plataforma de Autómatas y Lenguajes Formales

Proyecto final del curso **Autómatas y Lenguajes Formales** (UMG) — desarrollado por
**Ventura Software Solutions (VSS)**.

Simulador gráfico e interactivo de tres autómatas aplicados a problemas reales de Guatemala:

| Módulo | Técnica | Problema que resuelve |
|---|---|---|
| AFD | Autómata Finito Determinista | Validación sintáctica de NIT y CUI (SAT / RENAP) |
| AFND | Autómata Finito No Determinista | Búsqueda simultánea de palabras clave en textos legales |
| AP | Autómata de Pila | Validación de etiquetado balanceado en XML del Régimen FEL |

## Estructura

```
backend/    API en Python (FastAPI) con los tres motores de autómatas + pruebas (pytest)
frontend/   Interfaz web en React + TypeScript + Cytoscape.js
docs/       Documentación formal del proyecto (propuesta, cronograma, aspectos técnicos, AS-IS, TO-BE)
```

## Cómo ejecutarlo

**Backend**
```
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
pytest -q
uvicorn app.main:app --reload
```

**Frontend** (en otra terminal, con el backend corriendo)
```
cd frontend
npm install
npm run dev
```

Luego abre `http://localhost:5173`.

## Equipo

- Team Leader — arquitectura, dirección técnica
- Project Manager / QA — documentación, calidad, pruebas
- Desarrollador Senior — backend, frontend y algoritmos

Catedrático: Ing. Eddy Hernández · Universidad Mariano Gálvez de Guatemala
