from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Исправляет последовательности автоинкремента для всех таблиц'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Исправляем последовательность для таблицы devices
            cursor.execute("SELECT MAX(id) FROM devices;")
            max_id = cursor.fetchone()[0]
            
            if max_id is not None:
                cursor.execute(f"SELECT setval('devices_id_seq', {max_id});")
                self.stdout.write(
                    self.style.SUCCESS(f'Последовательность devices_id_seq сброшена на {max_id}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Таблица devices пуста')
                )
                
            # Проверяем другие таблицы
            tables_to_fix = [
                ('parts', 'parts_id_seq'),
                ('journal', 'journal_id_seq'),
            ]
            
            for table, sequence in tables_to_fix:
                try:
                    cursor.execute(f"SELECT MAX(id) FROM {table};")
                    max_id = cursor.fetchone()[0]

                    if max_id is not None:
                        cursor.execute(f"SELECT setval('{sequence}', {max_id});")
                        self.stdout.write(
                            self.style.SUCCESS(f'Последовательность {sequence} сброшена на {max_id}')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'Таблица {table} пуста')
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Ошибка с таблицей {table}: {e}')
                    )
