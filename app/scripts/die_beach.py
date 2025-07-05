import logging
import sys

# Настройка корневого логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Вывод в stdout
        # logging.FileHandler('/var/log/python.log')  # Дополнительно в файл
    ]
)

def print_die():
    logging.info('Die, mother fucker, die!')
    print('Die, mother fucker, die!')

if __name__=="__main__":
    print_die()