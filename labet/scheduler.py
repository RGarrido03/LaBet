from django_q.models import Schedule


def create_schedule(apps, schema_editor):
    if not Schedule.objects.filter(func='labet.tasks.perform_scraping_for_lebull').exists():
        Schedule.objects.create(
            func='labet.tasks.perform_scraping_for_lebull',
            schedule_type=Schedule.MINUTES,
            minutes=10,
            repeats=-1  # Repetições infinitas
        )

    if not Schedule.objects.filter(func='labet.tasks.perform_scraping_for_betano').exists():
        Schedule.objects.create(
            func='labet.tasks.perform_scraping_for_betano',
            schedule_type=Schedule.MINUTES,
            minutes=10,
            repeats=-1
        )

    if not Schedule.objects.filter(func='labet.tasks.perform_scraping_for_betclic').exists():
        Schedule.objects.create(
            func='labet.tasks.perform_scraping_for_betclic',
            schedule_type=Schedule.MINUTES,
            minutes=10,
            repeats=-1
        )

    if not Schedule.objects.filter(func='labet.tasks.perform_scraping_for_placard').exists():
        Schedule.objects.create(
            func='labet.tasks.perform_scraping_for_placard',
            schedule_type=Schedule.MINUTES,
            minutes=10,
            repeats=-1
        )
