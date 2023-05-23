# скрипт по формированию Пакета РД;
import xml.etree.ElementTree as ET

# Открываем XML-файл для чтения
xml_file = "data/8_27_202111_29_00PM/5 9 3 10/AccDocs/CheckList/20211011092922_4DDFC139-4341-4A65-A3CA-D0082D4797B8/4DDFC139-4341-4A65-A3CA-D0082D4797B8.xml"
tree = ET.parse(xml_file)
root = tree.getroot()

# Итерируемся по элементам object и создаем объекты на основе метаданных
for obj in root.findall('object'):
    # Извлекаем атрибуты объекта
    obj_id = obj.get('id')
    create_time = obj.get('createTime')
    modify_time = obj.get('modifyTime')
    status = obj.get('status')
    create_user = obj.get('createUser')
    modify_user = obj.get('modifyUser')

    # Создаем словарь со значениями атрибутов
    attr_dict = {}
    for attr in obj.find('attributes').findall('attribute'):
        attr_name = attr.get('name')
        attr_datatype = attr.get('datatype')
        attr_value = attr.get('value')
        attr_dict[attr_name] = {'datatype': attr_datatype, 'value': attr_value}

    # Создаем список файлов, связанных с объектом
    files_list = []
    for file in obj.find('files').findall('file'):
        file_id = file.get('id')
        file_name = file.get('name')
        file_size = file.get('size')
        file_hash = file.get('hash')
        file_path = file.get('path')
        files_list.append({'id': file_id, 'name': file_name, 'size': file_size, 'hash': file_hash, 'path': file_path})

    # Выводим созданный объект
    print({
        'id': obj_id,
        'createTime': create_time,
        'modifyTime': modify_time,
        'status': status,
        'createUser': create_user,
        'modifyUser': modify_user,
        'attributes': attr_dict,
        'files': files_list
    })
