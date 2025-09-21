import logging
import sys
#!/usr/bin/env python3
import os
import random
import string
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values


# Настройка корневого логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Вывод в stdout
        # logging.FileHandler('/var/log/python.log')  # Дополнительно в файл
    ]
)

def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# def get_db_connection():
#     dsn = os.getenv("DATABASE_URL")
#     if not dsn:
#         raise RuntimeError(
#             "DATABASE_URL не задан. "
#             "Либо задайте DATABASE_URL, либо передайте POSTGRES_* переменные в контейнер app."
#         )
#     # psycopg2 понимает DSN в формате postgresql://user:pass@host:port/dbname
#     return psycopg2.connect(dsn)

def get_db_connection():
    host = os.getenv("DB_HOST", "db")
    port = os.getenv("POSTGRES_PORT", 5432)
    dbname = os.getenv("POSTGRES_DB")
    user = os.getenv("POSTGRES_USER")
    pwd = os.getenv("POSTGRES_PASSWORD")
    print(f"DEBUG: connecting with host={host}, port={port}, dbname={dbname}, user={user}, password={'SET' if pwd else 'EMPTY'}")
    return psycopg2.connect(
        host=host, port=port, dbname=dbname, user=user, password=pwd
    )


def populate(n: int = 10):
    """
    Вставляет n строк с тестовыми данными в таблицу my_table.
    """
    conn = get_db_connection()
    conn.autocommit = True
    with conn.cursor() as cur:
        # Готовим список кортежей (name, created_at)
        now = datetime.utcnow()
        records = [
            (f"test_{random_string(6)}", now)
            for _ in range(n)
        ]
        # Используем execute_values для эффективной вставки сразу нескольких строк
        sql = """
            INSERT INTO my_table (name, created_at)
            VALUES %s
            RETURNING id;
        """
        execute_values(cur, sql, records)
        ids = [row[0] for row in cur.fetchall()]
        logging.info(f"Inserted {len(ids)} rows, IDs: {ids}")
    conn.close()

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Populate my_table with test data")
    p.add_argument("-n", "--number", type=int, default=10,
                   help="How many rows to insert")
    args = p.parse_args()
    populate(args.number)
    print('Строки удачно вставлены в БД')