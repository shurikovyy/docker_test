import logging
import sys
import psycopg2
import random
import time
from faker import Faker
from datetime import datetime, timedelta

# Настройка корневого логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Вывод в stdout
        # logging.FileHandler('/var/log/python.log')  # Дополнительно в файл
    ]
)
#!/usr/bin/env python3
import os
import random
import string
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values

def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", 5432),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
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
        print(f"Inserted {len(ids)} rows, IDs: {ids}")
    conn.close()

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Populate my_table with test data")
    p.add_argument("-n", "--number", type=int, default=10,
                   help="How many rows to insert")
    args = p.parse_args()
    populate(args.number)
