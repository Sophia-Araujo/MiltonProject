from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
import uvicorn

# ----------------------------------------------------
# 1. Configuração da Aplicação e Importações de DB
# ----------------------------------------------------
from models import Contact as PydanticContact, ContactBase # Renomeia o modelo Pydantic
from database import SessionLocal, create_db_and_tables # Importa as ferramentas de DB
from database import Contact as DBContact # Importa o modelo ORM do DB

app = FastAPI(
    title="Microserviço de Agendamento e Comunicação - MVP",
    description="API REST para gerenciar contatos e agendamentos.",
    version="0.1.0"
)

# Função para obter a sessão do banco de dados (Dependency Injection)
# O 'yield' garante que a sessão seja fechada automaticamente após a requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Hook para criar o DB e tabelas na inicialização
@app.on_event("startup")
def startup_event():
    create_db_and_tables()

# ----------------------------------------------------
# 2. Endpoints (CRUD Completo de Contatos - Agora com Persistência)
# ----------------------------------------------------

# Health Check (GET /)
@app.get("/")
def health_check():
    return {"status": "ok", "service": "Communication and Scheduling Microservice"}

# CREATE (POST /contacts/)
@app.post("/contacts/", response_model=PydanticContact, status_code=201, tags=["Contatos"])
# O parâmetro 'db' recebe a sessão do banco de dados
def create_contact(contact: ContactBase, db: Session = Depends(get_db)):
    """
    Registra um novo contato no sistema e o salva no banco de dados.
    """
    # 1. Verifica se o email já existe (Query no DB)
    db_contact = db.query(DBContact).filter(DBContact.email == contact.email).first()
    if db_contact:
        raise HTTPException(status_code=400, detail="Email já cadastrado.")

    # 2. Cria o objeto ORM e o adiciona ao DB
    db_contact = DBContact(**contact.model_dump())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact) # Garante que o ID gerado pelo DB seja populado

    return db_contact

# READ ALL (GET /contacts/)
@app.get("/contacts/", response_model=List[PydanticContact], tags=["Contatos"])
def list_contacts(db: Session = Depends(get_db)):
    """
    Lista todos os contatos registrados no banco de dados.
    """
    contacts = db.query(DBContact).all()
    return contacts

# READ BY ID (GET /contacts/{contact_id})
@app.get("/contacts/{contact_id}", response_model=PydanticContact, tags=["Contatos"])
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    """
    Busca um contato específico pelo ID.
    """
    db_contact = db.query(DBContact).filter(DBContact.id == contact_id).first()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contato não encontrado.")
    return db_contact

# UPDATE (PUT /contacts/{contact_id})
@app.put("/contacts/{contact_id}", response_model=PydanticContact, tags=["Contatos"])
def update_contact(contact_id: int, contact: ContactBase, db: Session = Depends(get_db)):
    """
    Atualiza todas as informações de um contato existente.
    """
    db_contact = db.query(DBContact).filter(DBContact.id == contact_id).first()
    
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contato não encontrado.")

    # Verifica unicidade do email, exceto o contato atual
    email_exists = db.query(DBContact).filter(
        DBContact.email == contact.email, 
        DBContact.id != contact_id
    ).first()
    if email_exists:
        raise HTTPException(status_code=400, detail="Outro contato já cadastrado com este email.")

    # Aplica as novas informações
    db_contact.name = contact.name
    db_contact.email = contact.email
    db_contact.phone = contact.phone
    
    db.commit()
    db.refresh(db_contact)
    
    return db_contact

# DELETE (DELETE /contacts/{contact_id})
@app.delete("/contacts/{contact_id}", status_code=204, tags=["Contatos"])
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    """
    Remove um contato do sistema.
    """
    db_contact = db.query(DBContact).filter(DBContact.id == contact_id).first()
    
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contato não encontrado.")
    
    db.delete(db_contact)
    db.commit()
    
    return