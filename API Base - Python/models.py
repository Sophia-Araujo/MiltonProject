from pydantic import BaseModel, Field
from typing import Optional

# Modelo base para criar/atualizar um Contato (Payload de entrada)
class ContactBase(BaseModel):
    # Field(...) indica que o campo é obrigatório
    name: str = Field(..., example="João Silva")
    email: str = Field(..., example="joao.silva@empresa.com")
    
    # Optional[str] indica que o campo é opcional
    phone: Optional[str] = Field(None, example="5511999998888")
    
# Modelo completo de Contato (Payload de resposta)
# Herda do ContactBase e adiciona o 'id', que é gerado pelo sistema
class Contact(ContactBase):
    id: int = Field(..., example=1)
    
    # Configuração Pydantic (necessário para o FastAPI serializar dados do Python)
    class Config:
        from_attributes = True