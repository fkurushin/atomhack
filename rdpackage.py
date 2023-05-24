import os
import xml.etree.ElementTree as ET
from functools import wraps
from loguru import logger
import json
from definitions import STANDART_DIR, TEST_DIR

logger.add("std.log", rotation="500 MB")
logger.info("Session started...")


def log_function(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Function {func.__name__} called with args={args}, kwargs={kwargs}")
    return wrapper


# лишние файлы не парные логгировать
@log_function
def parse_dir(path: str) -> dict:
    """
    Функция рекурсивно парсит директорию path и преобразует
    в словарь словарей
    :param path:
    :return:
    """
    result = {}
    dir_items = os.listdir(path)

    for item_name in dir_items:
        item_path = os.path.join(path, item_name)

        if os.path.isdir(item_path):
            result[item_name] = parse_dir(item_path)
        else:
            result[item_name] = None
    return result

def content2extension(path:str)->str:
    return path.split(".")[-1]

@log_function
def parse_xml(path: str) -> dict:
    """
    Функция парсит xml файл в словарь словарей
    :param path:
    :return:
    """
    tree = ET.parse(path)
    root = tree.getroot()

    result_dict = {}

    def find_element(element, dict_obj):
        for key, value in element.items():
            dict_obj[key] = value

        if element.text and element.text.strip():
            dict_obj['value'] = element.text.strip()

        for child_elem in element:
            child_dict = {}
            find_element(child_elem, child_dict)
            dict_obj[child_elem.tag] = child_dict

    find_element(root, result_dict)
    return result_dict


@log_function
def compare_dirs(dir1_path: str, dir2_path: str) -> bool:
    """
    Функция сравнивает две директории на соответствие структуре и содержанию пакету РД.
    Сначала проверяется accdocs, потом docs, в  accdocs надо учесть названия
    CheckList, IKL, Notes, PDTK, потом уже содержание этих директорий
    :param dir1_path: путь к первой директории
    :param dir2_path: путь ко второй директории
    :return: True, если директории совпадают, и False - в противном случае
    """
    dir1_content = parse_dir(dir1_path)
    dir2_content = parse_dir(dir2_path)

    if len(dir1_content) != len(dir2_content):
        logger.info(f"{dir1_content} contains {len(dir1_content)}, "
                    f"but {dir2_content} contains {len(dir2_content)}")


    # Сверяем наличие элементов и их содержание в двух директориях
    for item_name in dir1_content:
        if item_name not in dir2_content:

        item1_content = dir1_content[item_name]
        item2_content = dir2_content[item_name]

        # Если элемент является директорией, рекурсивно вызываем функцию сравнения для него
        if isinstance(item1_content, dict):
            if not compare_dirs(os.path.join(dir1_path, item_name), os.path.join(dir2_path, item_name)):
                logger.info()
        # Если элемент является файлом, проверяем совпадение их содержимого
        else:
            if item1_content != item2_content:
                logger.info()

    return True


if __name__ == "__main__":

   compare_dirs(STANDART_DIR, TEST_DIR)
