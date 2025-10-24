from fastapi import APIRouter, HTTPException
from typing import Optional
from service.mensagem_service import MensagemService
from service.scheduler import agendar_envio

router = APIRouter(prefix="/mensagem", tags=["Mensagens"])

@router.post("/enviar/")
def enviar_mensagem(canal: str, destinatario: str, conteudo: str, assunto: Optional[str] = None):
    service = MensagemService()
    ok = service.enviar_mensagem(canal, destinatario, conteudo, assunto)
    if not ok:
        raise HTTPException(status_code=500, detail="Falha ao enviar mensagem.")
    return {"status": "enviado", "canal": canal, "destinatario": destinatario}

@router.post("/agendar/")
def agendar_mensagem(canal: str, destinatario: str, conteudo: str, minutos: int = 1, assunto: Optional[str] = None):
    agendar_envio.apply_async(args=[canal, destinatario, conteudo, assunto], countdown=minutos * 60)
    return {"status": "agendado", "execução_em": f"{minutos} minuto(s)"}
