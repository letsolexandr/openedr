import os
import xml.etree.ElementTree as ET

import psutil

process = psutil.Process(os.getpid())
import pymongo
from client import DBClient

client = DBClient()

PATH = "/path/to/File1.xml"
PATH1 = "/path/to/File2.xml"


def get_child_nested(item):
    res = {}
    if item.getchildren():
        for child in item.getchildren():
            if hasattr(child, 'tag'):
                if child.getchildren():
                    res[getattr(child, 'tag')] = get_child_nested(child)
                else:
                    res[getattr(child, 'tag')] = getattr(child, 'text')
    else:
        res[getattr(item, 'tag')] =getattr(item, 'text')
    return res


def import_data(path: str):
    print('START')
    is_true = True
    processed = 1
    dublicate = 0
    insert = 0
    print('Processing')
    context = ET.iterparse(path, events=('start',))
    event, root = context.__next__()
    while is_true:
        try:
            event, elem = context.__next__()
            if getattr(elem, 'tag') == 'SUBJECT':
                dict_item = get_child_nested(elem)

                try:
                    client.import_item(dict_item)
                except pymongo.errors.DuplicateKeyError as e:
                    dublicate += 1
                finally:
                    dict_item = {}
                    if processed % 100000 == 0:
                        insert = processed - dublicate
                        print(f'Processed {processed}')
                        print(f'Skipped: {dublicate}')
                        print(f'Inserted: {insert}')
                        print('Memory usage: ', process.memory_percent())
                        print('-' * 20)
                    processed += 1
            elem.clear()
            root.clear()
        except StopIteration:
            print('END')
            is_true = False


import_data(PATH)
import_data(PATH1)
