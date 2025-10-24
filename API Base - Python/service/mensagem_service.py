from service.email_channel import EmailChannel
from service.whatsapp_channel import WhatsappChannel

class MensagemService:
    def __init__(self):
        self.email_channel = EmailChannel()
        self.whatsapp_channel = WhatsappChannel()

    def enviar_mensagem(self, canal: str, destinatario: str, conteudo: str, assunto: str = None):
        if canal.lower() == "email":
            self.email_channel.enviar(destinatario, assunto or "Notificação Automática", conteudo)
        elif canal.lower() == "whatsapp":
            self.whatsapp_channel.enviar(destinatario, conteudo)
        else:
            print(f"[ERRO] Canal '{canal}' não suportado.")
