import boto3
import csv
from botocore.exceptions import ClientError

## csv 내용 순서 : FromPort, ToPort, IpProtocol, CidrIp, IpRanges, Description
## 필수 입력 : 해당 고객사 리전, accsee key, secret key
access_key ='입력'
secret_access_key = '입력'
region = 'ap-northeast-2'
#VPC ID 입력
vpc_id_info = '입력'
##SG Name tag 입력
sg_name = '입력'
## csv 파일 경로 및 파일 이름
path = '입력'
# 예 ) "C:/Users/mydhdbrud/PycharmProjects/pythonProject/create_sg/csv_test.csv"



ec2 = boto3.resource('ec2',
                   aws_access_key_id=access_key,
                   aws_secret_access_key=secret_access_key,
                   region_name=region)

csv_file = path

vpc_id = vpc_id_info

# security_group이 존재할때
# security_group_id = "sg-000000000"
# security_group = ec2.SecurityGroup(security_group_id)


try:
    #SECURITY_GROUP_NAME 과 DESCRIPTION 입력 필요
    response = ec2.create_security_group(GroupName='test05',
                                         Description='test05',
                                         VpcId=vpc_id,
                                         TagSpecifications = [
                                             {
                                                 'ResourceType': 'security-group',
                                                 'Tags' : [
                                                     {
                                                         'Key': 'Name',
                                                         'Value': sg_name
                                                     }
                                                 ]
                                             }
                                         ]
                                         )


    f = open(csv_file, encoding= 'utf-8-sig')
    csv_f = csv.reader(f)
    #security_group.revoke_ingress(IpPermissions=security_group.ip_permissions)
    # 보안그룹에서 모든 룰 삭제시 사용

    for row in csv_f:
        port_range_start = row[0]
        port_range_end = row[1]
        protocol = row[2]
        cidr = row[3]
        IpRanges = row[4]
        description = row[5]

        response.authorize_ingress(
            DryRun=False,
            IpPermissions=[
                {
                    'FromPort': int(port_range_start),
                    'ToPort': int(port_range_end),
                    'IpProtocol': protocol,
                    'IpRanges': [
                        {
                            'CidrIp': cidr+''+IpRanges,
                            'Description': description
                        },
                    ]
                }
            ]
        )
except ClientError as e:
    print(e)