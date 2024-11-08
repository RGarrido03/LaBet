from django_q.models import Schedule
from django_q.tasks import schedule

# Agende a tarefa
schedule(
    'app.tasks.perform_scraping',
    schedule_type=Schedule.MINUTES,
    minutes=0.5,  # Execute a cada 12 segundos (0.2 minutos)
    repeats=-1  # Repetições infinitas
)
