from django.core.management.base import BaseCommand, CommandError
import os
import subprocess

from django.conf import settings
from django.core.management import call_command


class Command(BaseCommand):
    help = 'this helps to generate base questions'

    def handle(self, *args, **options):
        # Command logic here
        # Use self.stdout.write to print output
        db_name = settings.DATABASES['default']['NAME']
        db_user = settings.DATABASES['default']['USER']
        db_password = settings.DATABASES['default']['PASSWORD']
        db_host = settings.DATABASES['default']['HOST']

        base_dir = settings.BASE_DIR
        cmd_list = [
            'PGPASSWORD=' + db_password,
            'psql',
            '-U',
            db_user,
            '-h',
            db_host,
            '-d',
            db_name,
            '-f',
            (base_dir.parent / 'part1_questions.sql').as_posix(),
            '-f',
            (base_dir.parent / 'part2_questions.sql').as_posix(),
            '-f',
            (base_dir.parent / 'part3_questions.sql').as_posix(),
        ]
        process = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        self.stdout.write(process.stdout.decode('utf-8'))
        if process.returncode != 0:
            raise CommandError(f'Error: {repr(process.stderr.decode("utf-8"))}')

        self.stdout.write(self.style.SUCCESS('Successfully executed command'))
