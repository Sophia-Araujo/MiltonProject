# models.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# --- Pydantic Models (Entrada/Saída da API) ---
# ----------------------------------------------

# Modelo base para criar/atualizar um Contato (Payload de entrada)
class ContactBase(BaseModel):
    name: str = Field(..., example="João Silva")
    email: str = Field(..., example="joao.silva@empresa.com")
    canalPref: str = Field(..., example="Whatsapp")
    phone: Optional[str] = Field(None, example="5511999998888")
    codExterno: Optional[str] = Field(None, example="A0013")

# Modelo completo de Contato (Payload de resposta)
class Contact(ContactBase):
    id: int = Field(..., example=1)

    class Config:
        from_attributes = True  # Necessário para conversão ORM → Pydantic


# ---- Modelos de Cliente (para a API) ----
class ClienteBase(BaseModel):
    nome: str = Field(..., example="Empresa XPTO")
    email: str = Field(..., example="contato@empresa.com")
    telefone: Optional[str] = Field(None, example="11988887777")

class ClienteCreate(ClienteBase):
    pass

class ClienteOut(ClienteBase):
    id: int
    criado_em: datetime
    class Config:
        from_attributes = True


# ---- Modelos de Histórico de Mensagem (para a API) ----
class HistoricoBase(BaseModel):
    canal: str = Field(..., example="email")
    destinatario: str = Field(..., example="cliente@teste.com")
    conteudo: str = Field(..., example="Sua entrega foi confirmada.")
    status: Optional[str] = Field("PENDENTE", example="ENVIADO")

class HistoricoOut(HistoricoBase):
    id: int
    data_envio: datetime
    class Config:
        from_attributes = True


# --- SQLAlchemy ORM Models (Banco de Dados) ---
# ----------------------------------------------
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


# Tabela de Clientes
class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    telefone = Column(String, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    contatos = relationship("Contact", back_populates="cliente")




# Tabela de Histórico de Mensagens
class HistoricoMensagem(Base):
    __tablename__ = "historico_mensagens"

    id = Column(Integer, primary_key=True, index=True)
    canal = Column(String, nullable=False)
    destinatario = Column(String, nullable=False)
    conteudo = Column(Text, nullable=False)
    status = Column(String, default="PENDENTE")
    data_envio = Column(DateTime, default=datetime.utcnow)
