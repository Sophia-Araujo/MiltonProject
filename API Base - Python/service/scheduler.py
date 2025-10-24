from celery_app import celery_app
from service.mensagem_service import MensagemService

@celery_app.task
def agendar_envio(canal, destinatario, conteudo, assunto=None):
    """
    Tarefa Celery que executa o envio no horário agendado.
    """
    service = MensagemService()
    service.enviar_mensagem(canal, destinatario, conteudo, assunto)
