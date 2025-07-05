import logging
import sys
import pandas as pd

# Настройка корневого логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Вывод в stdout
        # logging.FileHandler('/var/log/python.log')  # Дополнительно в файл
    ]
)
def get_table():
    df = pd.DataFrame(columns=["name", "message"],
                      data=[['Sergey', 'genius'], ['Alex', 'terrorist']])
    return df
    
if __name__=="__main__":
    print(get_table())