import json

import openpyxl


data_list = []
key_list = []

excelName = 'filename.xlsx'

with open("filename.json", encoding='utf-8') as json_stream:
    dynamo_data = json.load(json_stream)


header = []

for key in dynamo_data[0].keys():
    header.append(key)

tuple(header)

for data in dynamo_data:

    value = []
    for values in data.values():
        value.append(values)
    tuple(value)
    data_list.append(value)


wb = openpyxl.Workbook()

sheet1 = wb.active
sheet1.append(header)

for data in data_list:
    print(data)
    sheet1.append(data)
wb.save(excelName)

