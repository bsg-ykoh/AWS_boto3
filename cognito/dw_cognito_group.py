import boto3
import datetime
from openpyxl import Workbook

access_key = ''
secret_key = ''
USER_POOL_ID = ''

#list_users_in_group

client = boto3.client('cognito-idp', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name='ap-northeast-2')
paginator = client.get_paginator('list_users_in_group')

response_iterator = paginator.paginate(
    UserPoolId=USER_POOL_ID,
    GroupName='users'

)




pageCount = 0
total = []
for a in response_iterator :
    pageCount += 1
    total += a['Users']

wb = Workbook()
ws = wb.active

# ###################### [header값 세팅] ######################
total0 = total[0]
total0Attributes = total0['Attributes']
header = ['Username']
header += ['sub']
header += ['birthdate']
header += ['email_verified']
header += ['custom:position']
header += ['custom:department']
header += ['custom:nationality']
header += ['custom:company']
header += ['custom:access_at']
header += ['custom:work_class']
header += ['custom:mobile']
header += ['custom:emp_type']
header += ['name']
header += ['custom:work_form']
header += ['email']
header += ['custom:blood_type']
header += ['UserCreateDate']
header += ['UserLastModifiedDate']
header += ['Enabled']
header += ['UserStatus']

# print('header : ', header)
ws.append(tuple(header))




# #################### [tableData값 세팅] ####################
for b in total :

    table = []

    table.append( b['Username'] )

    b_Attributes = b['Attributes']
    bloodColChk = 0
    for c in b_Attributes:
        if c['Name'] == 'custom:blood_type' :
            bloodColChk = 1
        table.append(c['Value'])

    # 혈액형 데이터가 없는경우 빈값 세팅
    if bloodColChk == 0 :
        table.append('-')

    DT1 = b['UserCreateDate']
    table.append(DT1.strftime('%Y-%m-%d %H:%M:%S %a'))
    DT2 = b['UserLastModifiedDate']
    table.append(DT2.strftime('%Y-%m-%d %H:%M:%S %a'))
    table.append(b['Enabled'])
    table.append(b['UserStatus'])

    ws.append(tuple(table))


excelName = 'cognito_data_users' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.xlsx'
wb.save(excelName)