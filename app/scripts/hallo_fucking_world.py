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

def print_greeting():
    logging.info('every 1 min: Shut up and smile!')
    print('print every 1 min: Shut up and smile!')

if __name__=="__main__":
    print_greeting()