import os
import xml.etree.ElementTree as ET
from loguru import logger
import json


# лишние файлы не парные логгировать

def parse_dir(path):
    result = {}
    dir_items = os.listdir(path)

    for item_name in dir_items:
        item_path = os.path.join(path, item_name)

        if os.path.isdir(item_path):
            result[item_name] = parse_dir(item_path)
        else:
            result[item_name] = None

    return result


def parse_xml(path):
    logger.add("std.log", )
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


if __name__ == "__main__":
    dir_path = 'data/8_27_202111_29_00PM'
    dir_dict = parse_dir(dir_path)
    with open('directory.json', 'w') as fp:
        json.dump(dir_dict, fp, indent=4)
    print(dir_dict)
    # print(parse_xml("data/8_27_202111_29_00PM/5 9 3 10/AccDocs/CheckList/20211011092922_4DDFC139-4341-4A65-A3CA-D0082D4797B8/4DDFC139-4341-4A65-A3CA-D0082D4797B8.xml"))