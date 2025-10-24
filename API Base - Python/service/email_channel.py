import smtplib
from email.mime.text import MIMEText
import os

class EmailChannel:
    def enviar(self, destinatario: str, assunto: str, conteudo: str):
        remetente = os.getenv("EMAIL_USER")
        senha = os.getenv("EMAIL_PASS")

        msg = MIMEText(conteudo, "plain", "utf-8")
        msg["Subject"] = assunto
        msg["From"] = remetente
        msg["To"] = destinatario

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(remetente, senha)
                server.send_message(msg)
            print(f"[EMAIL] Mensagem enviada para {destinatario}")
            return True
        except Exception as e:
            print(f"[EMAIL] Erro ao enviar: {e}")
            return False
