import os
import xml.etree.ElementTree as ET
from functools import wraps
from loguru import logger
import os
import json
import xmltodict
from collections import Counter
import json
from definitions import STANDART_DIR, TEST_DIR

logger.add("std.log", rotation="500 MB")
logger.info("Session started...")


def log_function(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info("Function {} called with args={}, kwargs={}", func.__name__, args, kwargs)
        result = func(*args, **kwargs)
        logger.info("Function {} returned {}", func.__name__, result)
        return result
    return wrapper


# лишние файлы не парные логгировать
# @log_function
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


def content2format(path:str)->str:
    return path.split(".")[-1]


# @log_function
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

        # Если элемент является списком, то сохраняем атрибуты в виде списка
        if element.findall('*'):
            list_dict = []
            for child_elem in element:
                child_dict = {}
                find_element(child_elem, child_dict)
                list_dict.append(child_dict)
            dict_obj[element.tag] = list_dict
        else:
            # Иначе сохраняем обычный элемент
            if element.text and element.text.strip():
                dict_obj['value'] = element.text.strip()
            for child_elem in element:
                child_dict = {}
                find_element(child_elem, child_dict)
                dict_obj[child_elem.tag] = child_dict

    find_element(root, result_dict)
    return result_dict


def compare_directory_with_json(dir_path, json_file):
    # Загружаем JSON-файл в виде словаря
    expected_structure = parse_dir()

    # Получаем список файлов и каталогов в указанной директории
    actual_structure = {}
    for root, dirs, files in os.walk(dir_path):
        node = actual_structure
        for dir_name in sorted(dirs):
            node[dir_name] = {}
            node = node[dir_name]
        for file_name in sorted(files):
            node[file_name] = None

    # Сравниваем ожидаемую структуру с фактической
    return compare_dicts(expected_structure, actual_structure)


def compare_dicts(dict1, dict2):
    """
    Рекурсивно сравнивает два словаря, игнорируя ключи, начинающиеся с '_'
    """
    for key in dict1:
        if key.startswith('_'):
            continue
        if key not in dict2:
            return False
        if isinstance(dict1[key], dict):
            if not isinstance(dict2[key], dict):
                return False
            if not compare_dicts(dict1[key], dict2[key]):
                return False
        elif dict1[key] is None:
            if dict2[key] is not None:
                return False
        else:
            # Проверяем, соответствует ли расширение файла ожидаемому формату
            expected_format = dict1[key]
            actual_format = os.path.splitext(key)[1]
            if not actual_format.endswith(expected_format):
                return False

    return True


# @log_function
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
        logger.info(f"{dir1_path} contains {len(dir1_content)}, "
                        f"but {dir2_path} contains {len(dir2_content)}")

    f1 = [content2format(d) for d in dir1_content]
    f2 = [content2format(d) for d in dir2_content]

    for item in f1:
        if item not in f2:
            logger.info(f"{item} is in list1, but not in list2")

    # Сверяем наличие элементов и их содержание в двух директориях
    for item_name in dir1_content:
        if item_name not in dir2_content:
            return False

        item1_content = dir1_content[item_name]
        item2_content = dir2_content[item_name]

        # Если элемент является директорией, рекурсивно вызываем функцию сравнения для него
        if isinstance(item1_content, dict):
            if not compare_dirs(os.path.join(dir1_path, item_name), os.path.join(dir2_path, item_name)):
                return False
        else:
            if item1_content != item2_content:
                return False

    return True


def compare_directory_with_json(dir_path, json_file, log_file):
    # Load the expected directory structure from JSON file
    with open(json_file) as f:
        expected_structure = json.load(f)
        print(expected_structure)

    # Walk through the actual directory structure and store it in a dictionary
    actual_structure = {}
    for root, dirs, files in os.walk(dir_path):
        node = actual_structure
        for dir_name in sorted(dirs):
            node[dir_name] = {}
            node = node[dir_name]
        for file_name in sorted(files):
            node[file_name] = None

    compare_dicts(expected_structure, actual_structure)


def compare_dicts(expected_dict, actual_dict, path=''):
    for key in expected_dict:
        expected_item = expected_dict[key]

        # Ignore keys that start with an underscore
        if key.startswith('_'):
            continue
        print(actual_dict)
        if key not in actual_dict:
            logger.warning(f'{path}/{key} is missing from the actual directory')
            continue

        actual_item = actual_dict[key]
        if isinstance(expected_item, dict) and isinstance(actual_item, dict):
            compare_dicts(expected_item, actual_item, f'{path}/{key}')
        elif expected_item is None:
            if actual_item is not None:
                logger.warning(f'{path}/{key} should be a file but is a directory')
        else:
            expected_extension = os.path.splitext(key)[1]
            if not actual_item:
                logger.warning(f'{path}/{key} is missing from the actual directory')
            elif not actual_item.endswith(expected_extension):
                logger.warning(f'{path}/{key} has an incompatible file format: {actual_item}')

        # Remove the item from the actual_dict so we can detect extra items
        del actual_dict[key]

    for key in actual_dict:
        if key.startswith('_'):
            continue
        logger.warning(f'{path}/{key} is an unexpected file or directory in the actual directory')


if __name__ == "__main__":
   compare_directory_with_json(TEST_DIR)

