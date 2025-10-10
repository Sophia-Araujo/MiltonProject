from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from typing import List, Optional
from sqlalchemy.orm import Session
import uvicorn
from fastapi.responses import StreamingResponse
import io
import csv

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
def create_contact(contact: ContactBase, db: Session = Depends(get_db)):
    """
    Registra um novo contato no sistema e o salva no banco de dados.
    """
    db_contact = db.query(DBContact).filter(DBContact.email == contact.email).first()
    if db_contact:
        raise HTTPException(status_code=400, detail="Email já cadastrado.")

    db_contact = DBContact(**contact.model_dump())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)

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

    email_exists = db.query(DBContact).filter(
        DBContact.email == contact.email, 
        DBContact.id != contact_id
    ).first()
    if email_exists:
        raise HTTPException(status_code=400, detail="Outro contato já cadastrado com este email.")
    cod_exists = db.query(DBContact).filter(
    DBContact.codExterno == contact.codExterno, 
    DBContact.id != contact_id
    ).first()
    if contact.codExterno: # Verifica apenas se o valor não é None
        cod_exists = db.query(DBContact).filter(
            DBContact.codExterno == contact.codExterno, 
            DBContact.id != contact_id
        ).first()
        if cod_exists:
            raise HTTPException(status_code=400, detail="Outro contato já cadastrado com este Código Externo.")

    # Aplica as novas informações
    db_contact.name = contact.name
    db_contact.email = contact.email
    db_contact.phone = contact.phone
    # Assumindo que 'codExterno' foi adicionado ao ContactBase:
    # db_contact.codExterno = contact.codExterno 
    db_contact.codExterno = contact.codExterno
    db_contact.canalPref = contact.canalPref
    db.commit()
    db.refresh(db_contact)
    
    return db_contact

# ENDPOINT: READ BY External Code (GET /contacts/external/{external_code})
@app.get("/contacts/external/{external_code}", response_model=PydanticContact, tags=["Contatos"])
def read_contact_by_external_code(external_code: str, db: Session = Depends(get_db)):
    """
    Busca um contato específico pelo Código Externo (codExterno).
    """
    db_contact = db.query(DBContact).filter(DBContact.codExterno == external_code).first()
    
    if db_contact is None:
        raise HTTPException(status_code=404, detail=f"Contato com código externo '{external_code}' não encontrado.")
    
    return db_contact

#ENDPOINT: Exportação de Contatos (CSV)
@app.get("/contacts/export/csv", tags=["Contatos"])
def export_contacts_to_csv(
    # Adicionamos o parâmetro opcional contact_id
    contact_id: Optional[int] = None, 
    db: Session = Depends(get_db)
):
    """
    Exporta contatos para um arquivo CSV.
    Se contact_id for fornecido, exporta apenas o contato com aquele ID.
    Caso contrário, exporta todos os contatos.
    """
    
    if contact_id is None:
        # Busca TODOS os contatos
        contacts = db.query(DBContact).all()
        filename = "todos_contatos_exportados.csv"
        
    else:
        # Busca APENAS o contato com o ID fornecido
        contact = db.query(DBContact).filter(DBContact.id == contact_id).first()
        
        if contact is None:
            raise HTTPException(status_code=404, detail=f"Contato com ID {contact_id} não encontrado para exportação.")
            
        contacts = [contact]  # Coloca o único contato em uma lista para iterar
        filename = f"contato_{contact_id}_exportado.csv"


    # Se a busca não encontrou nada (ex: lista vazia quando contact_id é None, 
    # ou 404 já foi lançado quando ID não existe)
    if not contacts:
        return {"message": "Nenhum contato para exportar."}


    # --- Lógica de Geração do CSV (Não precisa mudar) ---
    output = io.StringIO()
    fieldnames = ['id', 'name', 'email', 'phone',  'canalPref', 'codExterno'] 
    writer = csv.DictWriter(output, fieldnames=fieldnames)

    writer.writeheader()
    
    for contact in contacts:
        writer.writerow({
            'id': contact.id,
            'name': contact.name,
            'email': contact.email,
            'phone': contact.phone,
            'canalPref': contact.canalPref,
            'codExterno': contact.codExterno 
        })
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
#ENDPOINT: Importação de Contatos (CSV)
@app.post("/contacts/import/csv", tags=["Contatos"])
def import_contacts_from_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Importa contatos a partir de um arquivo CSV.
    Campos esperados no CSV: name, email, phone, codExterno
    """
    if file.content_type != 'text/csv':
        raise HTTPException(status_code=400, detail="Tipo de arquivo inválido. Por favor, envie um arquivo CSV.")

    content = file.file.read().decode('utf-8')
    csv_file = io.StringIO(content)
    reader = csv.DictReader(csv_file)

    imported_count = 0
    errors = []
    
    for row in reader:
        try:
            # Tenta criar um objeto Pydantic para validação inicial
            contact_data = ContactBase(
                name=row['name'],
                email=row['email'],
                phone=row['phone'],
                codExterno=row['codExterno']
            )
            
            # Verifica unicidade do email no DB (evita duplicatas)
            db_contact = db.query(DBContact).filter(DBContact.email == contact_data.email).first()
            if db_contact:
                errors.append(f"Email '{contact_data.email}' já existe e foi ignorado.")
                continue

            # Cria e adiciona o contato
            new_db_contact = DBContact(**contact_data.model_dump())
            db.add(new_db_contact)
            imported_count += 1
            
        except Exception as e:
            errors.append(f"Erro ao processar linha (Email/codExterno: {row.get('email', 'N/A')}/{row.get('codExterno', 'N/A')}): {e}")

    db.commit()
    
    return {
        "status": "sucesso",
        "total_imported": imported_count,
        "total_errors": len(errors),
        "errors": errors
    }

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