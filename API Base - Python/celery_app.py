from celery import Celery

# Conexão com Redis (broker + backend)
celery_app = Celery(
    "mensagens",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.conf.timezone = "America/Sao_Paulo"
celery_app.conf.task_serializer = "json"
