"""
Management command to migrate data from the old Flask/SQLAlchemy SQLite database
to the new Django database.

Usage:
    python manage.py import_flask_db --source data/database.db

What gets migrated:
    - animal_type, feeding_type, history_type
    - terrarium_type, terrarium_history_type
    - animals, feedings, history
    - terrariums, terrarium_equipment, terrarium_lamps, terrarium_history
    - documents, settings, notifications
    - users (with password hash conversion)

Password handling:
    Flask-Bcrypt hashes ($2b$...) are stored with Django's bcrypt hasher prefix.
    Requires: pip install django[bcrypt]
    If bcrypt is not available, user passwords are invalidated and must be reset.
"""

import sqlite3
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction


TABLES_DIRECT = [
    # (old_table, new_table)  — copied 1:1
    ('animal_type',           'animal_type'),
    ('feeding_type',          'feeding_type'),
    ('history_type',          'history_type'),
    ('terrarium_type',        'terrarium_type'),
    ('terrarium_history_type','terrarium_history_type'),
    ('animals',               'animals'),
    ('feedings',              'feedings'),
    ('history',               'history'),
    ('terrariums',            'terrariums'),
    ('terrarium_equipment',   'terrarium_equipment'),
    ('terrarium_lamps',       'terrarium_lamps'),
    ('terrarium_history',     'terrarium_history'),
    ('documents',             'documents'),
    ('settings',              'settings'),
    ('notifications',         'notifications'),
]


def table_exists(cursor, table_name):
    cursor.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    return cursor.fetchone()[0] > 0


def get_columns(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]


def convert_password(old_hash):
    """
    Convert Flask-Bcrypt hash ($2b$...) to Django's bcrypt format.
    Django expects: 'bcrypt$$2b$...'
    """
    if isinstance(old_hash, (bytes, bytearray)):
        old_hash = old_hash.decode('utf-8')
    if old_hash and old_hash.startswith('$2'):
        return f'bcrypt${old_hash}'
    return old_hash  # already in some other format


class Command(BaseCommand):
    help = 'Import data from old Flask SQLite database into Django database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            required=True,
            help='Path to the old Flask database.db file',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data in Django DB before import (use with caution!)',
        )

    def handle(self, *args, **options):
        source_path = options['source']

        try:
            src_conn = sqlite3.connect(source_path)
            src_conn.row_factory = sqlite3.Row
            src = src_conn.cursor()
        except Exception as e:
            raise CommandError(f'Cannot open source database: {e}')

        self.stdout.write(f'Importing from: {source_path}')

        connection.disable_constraint_checking()
        with transaction.atomic():
            dst = connection.cursor()

            if options['clear']:
                self.stdout.write(self.style.WARNING('Clearing existing data...'))
                for _, new_table in reversed(TABLES_DIRECT):
                    if self._django_table_exists(dst, new_table):
                        dst.execute(f'DELETE FROM "{new_table}"')
                if self._django_table_exists(dst, 'accounts_user'):
                    dst.execute('DELETE FROM accounts_user')

            # --- Copy data tables ---
            for old_table, new_table in TABLES_DIRECT:
                if not table_exists(src, old_table):
                    self.stdout.write(self.style.WARNING(f'  Skipping {old_table} (not found in source)'))
                    continue

                if not self._django_table_exists(dst, new_table):
                    self.stdout.write(self.style.WARNING(f'  Skipping {new_table} (not in Django DB — run migrate first)'))
                    continue

                src_cols = get_columns(src, old_table)
                dst_cols = self._get_django_columns(dst, new_table)

                # Only copy columns that exist in both tables
                common_cols = [c for c in src_cols if c in dst_cols]

                src.execute(f'SELECT {", ".join(common_cols)} FROM {old_table}')
                rows = src.fetchall()

                if not rows:
                    self.stdout.write(f'  {old_table}: 0 rows (empty)')
                    continue

                placeholders = ', '.join(['%s'] * len(common_cols))
                col_list = ', '.join(common_cols)
                insert_sql = f'INSERT OR IGNORE INTO "{new_table}" ({col_list}) VALUES ({placeholders})'

                count = 0
                for row in rows:
                    try:
                        dst.execute(insert_sql, tuple(row[c] for c in common_cols))
                        count += 1
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'    Row skipped: {e}'))

                self.stdout.write(self.style.SUCCESS(f'  {old_table}: {count}/{len(rows)} rows imported'))

            # --- Migrate users ---
            self._migrate_users(src, dst)

            # Fix 0-values in optional FK columns → NULL
            dst.execute("UPDATE animals SET default_ft = NULL WHERE default_ft = 0 OR default_ft = ''")
            dst.execute("UPDATE animals SET terrarium = NULL WHERE terrarium = 0 OR terrarium = ''")

        connection.enable_constraint_checking()
        src_conn.close()
        self.stdout.write(self.style.SUCCESS('\nImport complete!'))
        self.stdout.write(
            'NOTE: Run "python manage.py migrate --fake-initial" if you see migration conflicts.'
        )

    def _migrate_users(self, src, dst):
        if not table_exists(src, 'user'):
            self.stdout.write(self.style.WARNING('  Skipping user table (not found)'))
            return

        src.execute('SELECT id, email, password, is_admin, is_active, lang FROM user')
        users = src.fetchall()

        if not users:
            self.stdout.write('  user: 0 rows (empty)')
            return

        count = 0
        for u in users:
            email = u['email']
            username = email.split('@')[0]  # generate username from email
            password = convert_password(u['password'])
            is_staff = bool(u['is_admin'])
            is_active = bool(u['is_active'])
            lang = u['lang'] or 'en'

            try:
                dst.execute(
                    '''INSERT OR IGNORE INTO accounts_user
                       (id, username, email, password, is_staff, is_superuser,
                        is_active, lang, date_joined, first_name, last_name)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, datetime('now'), '', '')''',
                    (u['id'], username, email, password, is_staff, is_staff,
                     is_active, lang)
                )
                count += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'    User {email} skipped: {e}'))

        self.stdout.write(self.style.SUCCESS(f'  user → accounts_user: {count}/{len(users)} imported'))

        if count > 0:
            self.stdout.write(self.style.WARNING(
                '  Passwords converted to bcrypt format. Install django[bcrypt] if not done:\n'
                '    pip install django[bcrypt]\n'
                '  And add to settings.py PASSWORD_HASHERS:\n'
                "    'django.contrib.auth.hashers.BCryptPasswordHasher'"
            ))

    def _django_table_exists(self, cursor, table_name):
        cursor.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=%s",
            (table_name,)
        )
        return cursor.fetchone()[0] > 0

    def _get_django_columns(self, cursor, table_name):
        cursor.execute(f'PRAGMA table_info("{table_name}")')
        return [row[1] for row in cursor.fetchall()]
