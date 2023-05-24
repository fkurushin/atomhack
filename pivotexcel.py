# скрипт по формированию сводного excel-файла по всем Ведомостям Пакетов РД.
import os
# 1) все ок
# 2) незначительные изменения
# 3) куча файлов без структуры
# 4) изменены данные и метаданные

# excel сравнить с документацией с 4 пунктом контрактная спецификация

# exe шник и директорию будет пихать туда
import csv
import xml.etree.ElementTree as ET
from rdpackage import parse_xml
from loguru import logger

logger.add("std.log", rotation="500 MB")
logger.info("Session started...")


def check_filename(filename):
    """
    Требования из задания: «Файл Ведомости Пакета РД должен соответствовать следующим требованиям:
    •	иметь код WP в 4-м секторе;
    •	иметь расширение .doc/.docx;
    •	оканчиваться на цифру (0,1,2,3 и т.д) – это номер ревизии Ведомости;
    Дополнительно (необязательно):
    •	иметь перед цифрой символ r (НЕ e) – это язык ведомости пакета, то есть ведомость на русском»

    Функция для проверки имени файла с ведомостью пакета РД.
    Возвращает True, если имя файла соответствует требованиям, и False в противном случае.
    """
    if not filename.lower().endswith('.doc') and not filename.lower().endswith('.docx'):
        return False

    if not filename.split(".")[-2][-1].isdigit():
        return False

    if 'WP' != filename.split()[5]:
        return False

    return True


def xml_to_csv(xml_file, csv_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        writer.writerow(['tag_name', 'attribute_name', 'attribute_value'])

        for elem in root.iter():
            tag_name = elem.tag

            if tag_name in ['attribute', 'row']:
                attribute_name = elem.attrib.get('name')
                attribute_value = elem.attrib.get('value', elem.text)
                writer.writerow([tag_name, attribute_name, attribute_value])


def find_doc_in_xml(path:str)->bool:
    d = parse_xml(path)
    file_name = d["object"][1]["files"][0]["name"]
    if check_filename(file_name):
        logger.info(f"File name '{file_name}' matches the requirements.")
        return True
    else:
        logger.info(f"File name '{file_name}' does not match the requirements.")
        return False


def create_csv(path:str, csv_file:str):
    if find_doc_in_xml(path):
        xml_to_csv(path, csv_file)
        logger.info(f"Succesfully wrote data from {path} to {csv_file}")
    else:
        logger.info("Pass")


if __name__ == "__main__":
    # Пример использования функции
    create_csv("data/8_27_202111_29_00PM/5 9 3 10/B3A356AD-6615-4842-9787-7369103404C0.xml")