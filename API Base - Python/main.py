from fastapi import FastAPI, HTTPException
from typing import List, Optional

# Importa os modelos definidos
from models import Contact, ContactBase 

# ----------------------------------------------------
# 1. Configuração da Aplicação e Armazenamento em Memória
# ----------------------------------------------------
app = FastAPI(
    title="Microserviço de Agendamento e Comunicação - MVP",
    description="API REST para gerenciar contatos e agendamentos.",
    version="0.1.0"
)

# Simulação de Banco de Dados (In-Memory para o MVP inicial)
in_memory_contacts: List[Contact] = []
next_id = 1

# Função auxiliar para encontrar um contato e retornar o índice
def get_contact_index(contact_id: int) -> int:
    """Busca o índice do contato na lista, levanta 404 se não encontrado."""
    try:
        index = next(i for i, c in enumerate(in_memory_contacts) if c.id == contact_id)
        return index
    except StopIteration:
        raise HTTPException(status_code=404, detail="Contato não encontrado.")


# ----------------------------------------------------
# 2. Endpoints (CRUD Completo de Contatos)
# ----------------------------------------------------

# Health Check (GET /)
@app.get("/")
def health_check():
    """Verifica o status da API."""
    return {"status": "ok", "service": "Communication and Scheduling Microservice"}

# CREATE (POST /contacts/)
@app.post("/contacts/", response_model=Contact, status_code=201, tags=["Contatos"])
def create_contact(contact: ContactBase):
    """
    Registra um novo contato no sistema.
    """
    global next_id
    
    # Verifica se o email já existe (simulação de unicidade)
    if any(c.email.lower() == contact.email.lower() for c in in_memory_contacts):
        raise HTTPException(
            status_code=400, detail="Email já cadastrado."
        )

    # Cria o novo objeto Contact com o ID
    new_contact = Contact(id=next_id, **contact.model_dump())
    in_memory_contacts.append(new_contact)
    next_id += 1
    
    return new_contact

# READ ALL (GET /contacts/)
@app.get("/contacts/", response_model=List[Contact], tags=["Contatos"])
def list_contacts():
    """
    Lista todos os contatos registrados.
    """
    return in_memory_contacts

# READ BY ID (GET /contacts/{contact_id})
@app.get("/contacts/{contact_id}", response_model=Contact, tags=["Contatos"])
def read_contact(contact_id: int):
    """
    Busca um contato específico pelo ID.
    """
    index = get_contact_index(contact_id)
    return in_memory_contacts[index]

# UPDATE (PUT /contacts/{contact_id})
@app.put("/contacts/{contact_id}", response_model=Contact, tags=["Contatos"])
def update_contact(contact_id: int, contact: ContactBase):
    """
    Atualiza todas as informações de um contato existente.
    """
    index = get_contact_index(contact_id)
    
    # Verifica unicidade do email, exceto o contato atual
    if any(c.email.lower() == contact.email.lower() and c.id != contact_id for c in in_memory_contacts):
        raise HTTPException(
            status_code=400, detail="Outro contato já cadastrado com este email."
        )

    # Cria um objeto Contact atualizado, mantendo o ID original
    updated_contact = Contact(id=contact_id, **contact.model_dump())
    in_memory_contacts[index] = updated_contact
    
    return updated_contact

# DELETE (DELETE /contacts/{contact_id})
@app.delete("/contacts/{contact_id}", status_code=204, tags=["Contatos"])
def delete_contact(contact_id: int):
    """
    Remove um contato do sistema.
    """
    index = get_contact_index(contact_id)
    in_memory_contacts.pop(index)
    
    # Retorna 204 No Content, que é o padrão para DELETE bem-sucedido
    return