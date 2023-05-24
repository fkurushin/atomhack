from loguru import logger
import os
import re
import xml.etree.ElementTree as ET
import lxml.etree as etree
import shutil
from pathlib import Path


from definitions import *

logger.add("std.log", rotation="500 MB")
logger.info("Session started...")


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

        if element.findall('*'):
            list_dict = []
            for child_elem in element:
                child_dict = {}
                find_element(child_elem, child_dict)
                list_dict.append(child_dict)
            dict_obj[element.tag] = list_dict
        else:
            if element.text and element.text.strip():
                dict_obj['value'] = element.text.strip()
            for child_elem in element:
                child_dict = {}
                find_element(child_elem, child_dict)
                dict_obj[child_elem.tag] = child_dict

    find_element(root, result_dict)
    return result_dict


def compare_directories(expected_dict, actual_dict):
    if expected_dict == actual_dict:
        return True

    for key in expected_dict.keys():
        if key not in actual_dict.keys():
            logger.error(f"Directory {key} is missing in actual directory")
            continue

        if isinstance(expected_dict[key], str):
            if expected_dict[key] != actual_dict[key]:
                logger.error(f"File {key}/{expected_dict[key]} does not match in actual directory")
            continue

        if isinstance(expected_dict[key], dict):
            if not compare_directories(expected_dict[key], actual_dict[key]):
                logger.error(f"Subdirectory {key} contents do not match in actual directory")
                continue

    return True


def get_directory_structure(rootdir):
    """
    Creates a nested dictionary that represents the folder structure of rootdir
    """
    directory = {}
    rootdir = rootdir.rstrip(os.sep)

    for path, dirs, files in os.walk(rootdir):
        folders = os.path.relpath(path, rootdir).split(os.sep)
        parent = directory

        for folder in folders:
            parent = parent.setdefault(folder, {})

        for file in files:
            parent[file] = None

    return directory


def check_supporting_files(actual_dict):
    for subdir in actual_dict.keys():
        if isinstance(actual_dict[subdir], dict):
            check_supporting_files(actual_dict[subdir])
        elif isinstance(actual_dict[subdir], str) and os.path.splitext(actual_dict[subdir])[1] == '.xml':
            xml_file_path = os.path.join(subdir, actual_dict[subdir])
            base_file_name = os.path.splitext(xml_file_path)[0]
            supporting_files = [base_file_name + ext for ext in ('.files', '.log')]
            for supporting_file in supporting_files:
                if not os.path.exists(supporting_file):
                    logger.error(f"File {supporting_file} is missing")
    logger.info(f"All .files have their .log")


def validate_xml_files(actual_path):
    for subdir, dirs, files in os.walk(actual_path):
        for file_name in files:
            if os.path.splitext(file_name)[1] == ".xml":
                file_path = os.path.join(subdir, file_name)
                try:
                    parser = etree.XMLParser()
                    tree = etree.parse(file_path, parser)
                except Exception as e:
                    logger.error(f"Error while parsing {file_path}: {e}")


def create_directories(base_path, directory_dict):
    for name in directory_dict.keys():
        path = os.path.join(base_path, name)
        os.makedirs(path, exist_ok=True)
        subdirs = directory_dict[name]
        if subdirs:
            create_directories(path, subdirs)


def get_files_list(directory_path):
    files_dict = {}

    for file_name in os.listdir(directory_path):
        name, ext = os.path.splitext(file_name)
        file_format = name + ext
        if name in files_dict:
            files_dict[name].append(file_format)
        else:
            files_dict[name] = [file_format]

    result = []
    for name, formats in files_dict.items():
        if len(formats) == 2:
            result.append(formats)
        else:
            logger.info(f'Нет пары файлов с одинаковым именем в директории {formats}')

    return result


def move2(src_path, dest_path):
    """
    src_path - путь к исходному файлу
    dest_path - путь к целевой директории
    """
    if os.path.isfile(src_path):
        os.makedirs(dest_path, exist_ok=True)
        shutil.copy(src_path, dest_path)
        logger.info(f"File {src_path} moved to {dest_path}")
    else:
        logger.info(f"File {src_path} doesn't exist")


def move_files_by_attribute(directory_path:str):
    # здесь же создам директории
    file_list = get_files_list(directory_path)
    create_directories(".", DIR)
    # Определяем метку для первого цикла
    xml_loop_label = 'xml_loop'

    for xml, files in file_list:
        xml_path = directory_path + "/" + xml
        files_path = directory_path + "/" + files
        txt = Path(xml_path).read_text()
        for key, value in ATTRIBUTE_MAP.items():
            if key in txt:
                move2(xml_path,
                      list(DIR.keys())[0] + "/AccDocs/" + value+"/" + xml)
                move2(files_path,
                      list(DIR.keys())[0] + "/AccDocs/" + value + "/" + xml)
                # Переходим к следующей итерации первого цикла
                continue
                xml_loop_label

        move2(xml_path,
              list(DIR.keys())[0] + "/Docs/" + xml)
        move2(files_path,
              list(DIR.keys())[0] + "/AccDocs/" + value + "/" + xml)


if __name__ == "__main__":

   # # 1) парсинг и сравнение директорий
   # expected_structure = get_directory_structure(STANDART_DIR)
   # actual_structure = get_directory_structure(TEST_DIR)
   # compare_directories(expected_structure, actual_structure)
   #
   # # 2) Валидация xml файлов
   # validate_xml_files(TEST_DIR)

   #  3) Структурирование
   directory_path = "test_data_1"

   move_files_by_attribute("test_data_1")

   # print(get_files_list(directory_path))
   # to AccDocs
   # map = {"Чек-лист": "CheckList",
   #        "Сопроводительное письмо": "IKL",
   #        "Explanatory Note": "Notes",
   #        "ПДТК": "PDTK"}
   # # rest to Docs
   # dir = {
   #     "1 2 3 4": {
   #      "AccDocs": ["PDTK", "IKL", "Notes", "CheckList"],
   #      "Docs": []
   #      }
   # }
   # check_supporting_files(actual_structure)