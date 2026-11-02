from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

app = FastAPI(title="Muro de Eugenio")
templates = Jinja2Templates(directory="templates")


# ---------- DATOS (en memoria: se pierden al reiniciar el servidor) ----------
MENSAJES = [
    {"id": 1, "autor": "Ane", "texto": "Bienvenidos al muro de 2.º DAM", "observaciones": "Observación de Ane"},
    {"id": 2, "autor": "Iker", "texto": "¿Alguien ha conseguido arrancar uvicorn?", "observaciones": "Observación de Iker"},
]

def siguiente_id():
    return max((m["id"] for m in MENSAJES), default=0) + 1

class MensajeNuevo(BaseModel):
    autor: str = Field(min_length=1, max_length=30)
    texto: str = Field(min_length=1, max_length=280)
    observaciones: str = Field(min_length=1, max_length=280)



# 1. GET /salud → {"ok": True, "app": "Muro"}

@app.get("/salud")
def salud():
    return {"ok": True, "app": "Muro"}


@app.get("/hola/{nombre}")
def hola(nombre: str):
    return {"saludo": f"Hola, {nombre}"}

@app.post("/")
def publicar(autor: str = Form(""), texto: str = Form(""), observaciones:str = Form("")):
    MENSAJES.append({"id": siguiente_id(), "autor": autor, "texto": texto, "observaciones":observaciones})
    return RedirectResponse("/", status_code=303)



# ---------- API (JSON) ----------
@app.get("/api/mensajes")
def listar_mensajes():
    return MENSAJES

@app.get("/api/mensajes/{mensaje_id}")
def ver_mensaje(mensaje_id: int):
    for m in MENSAJES:
        if m["id"] == mensaje_id:
            return m
    raise HTTPException(status_code=404, detail="No existe ese mensaje")

@app.post("/api/mensajes", status_code=201)
def crear_mensaje(nuevo: MensajeNuevo):
    mensaje = {"id": siguiente_id(), **nuevo.model_dump()}
    MENSAJES.append(mensaje)
    return mensaje

# ---------- PÁGINAS (HTML) ----------
@app.get("/", response_class=HTMLResponse)
def inicio(request: Request):
    return templates.TemplateResponse(request, "index.html", {"mensajes": MENSAJES})

@app.get("/mensajes/{mensaje_id}", response_class=HTMLResponse)
def detalle(request: Request, mensaje_id: int):
    for m in MENSAJES:
        if m["id"] == mensaje_id:
            return templates.TemplateResponse(request, "mensaje.html", {"mensaje": m})
    raise HTTPException(status_code=404, detail="No existe ese mensaje")



# ---------- PRUEBA (en el Aula; en tu ordenador: python main.py) ----------
if __name__ == "__main__":
    from aula import Cliente
    c = Cliente(app)
    print(c.get("/salud").json())