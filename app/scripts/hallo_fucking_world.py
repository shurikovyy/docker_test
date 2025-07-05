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
    logging.info('* Shut up and smile!')

if __name__=="__main__":
    try:
        print_greeting()
    except Exception as e:
        logging.exception("Error in hallo_fucking_world.py")
        sys.exit(1)