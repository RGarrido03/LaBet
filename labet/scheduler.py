from django_q.models import Schedule


def create_schedule(apps, schema_editor):
    if not Schedule.objects.filter(func='labet.tasks.perform_scraping').exists():
        Schedule.objects.create(
            func='labet.tasks.perform_scraping',
            schedule_type=Schedule.MINUTES,
            minutes=10,  # Execute a cada 10 MIN
            repeats=-1  # Repetições infinitas
        )
        # Add another schedule and then run migration
