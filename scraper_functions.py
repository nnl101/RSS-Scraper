import json
import time
from datetime import datetime
from time import mktime
import itertools
import os
import requests

def open_json(json_file):
    with open(json_file, "r") as read_file:
        return json.load(read_file)

def write_to_json(json_file, json_data):
    with open(json_file, 'w', encoding ='utf-8') as fout:
        return json.dump(json_data, fout, ensure_ascii=False, indent=4)

#searches a list of dictionaries and returns a value
def ind_search(comp_id: object, value: object, list_of_dictionaries: object) -> object:
    for item in list_of_dictionaries:
        if item['ID'] == comp_id:
            return item[value]

#searches a list of dictionaries and returns a dictionary
def dic_search(key, value, list_of_dictionaries):
    return [element for element in list_of_dictionaries if element[key] == value]

#converts time.struct_time objects into strings so that they are json-compatible
def convert_to_ts(time_struct_object):
    if type(time_struct_object) == time.struct_time:
        time_string = time.strftime('%Y-%m-%d %H:%M:%S', time_struct_object)
        return time_string

#converts time.struct_time objects into YYYYMMDD string format
def time_to_str(ts_object):
   if type(ts_object) == time.struct_time:
       dt = datetime.fromtimestamp(mktime(ts_object))
       dt = dt.strftime('%Y%m%d')
       return dt

#takes a list of dictionaries, updates its values based off another dict or appends the dict if it is not already in the list of dictionaries
def update_checked(list_of_dictionaries,new_dictionary):
    site_previously_checked_yet = False

    for dict in list_of_dictionaries:
        if dict['ID'] == new_dictionary['ID']:
            if 'date' in dict.keys():
                site_previously_checked_yet = True
                return dict.update(new_dictionary)

    if site_previously_checked_yet == False:
        return list_of_dictionaries.append(new_dictionary)

#creates the last_updated nested dictionary
class NestedDict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value

def notify(json_data):
    notify_data = {'status': 200, 'items': json_data}
    headers = {'Authorization': 'dykhPFIs^E7#ppuu'}
    response = requests.post('https://imd.crimmond-associates.co.uk/notify/', headers = headers, data=json.JSONEncoder().encode((notify_data)))
    print(response.raise_for_status)
    print(response.content)