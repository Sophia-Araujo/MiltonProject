from fastapi import FastAPI
from database import create_db_and_tables
from routes import contacts, mensagens
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Microserviço de Agendamento e Comunicação",
    description="Gerencia contatos, envio e agendamento de mensagens.",
    version="1.0.0"
)

@app.on_event("startup")
def startup():
    create_db_and_tables()

# Inclui rotas
app.include_router(contacts.router)
app.include_router(mensagens.router)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "Communication and Scheduling API"}
