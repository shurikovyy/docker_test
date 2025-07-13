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
def nu_ti_stas():
    logging.warning('** Stasik - pidarasik! **')

if __name__=="__main__":
    nu_ti_stas()