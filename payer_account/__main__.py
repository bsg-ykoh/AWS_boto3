import json

import boto3
import payer_account_set.boto3_func as func

### 반드시 이름은 소문자로만 입력해 주세요
new_name = 'samoo'

new_payer_account_id = ''
new_payer_access_key = ''
new_payer_secret_key = ''
new_payer_region = 'ap-northeast-2'

billing_access_key = ''
billing_secret_key = ''


iam_client = boto3.client('iam',aws_access_key_id=new_payer_access_key, aws_secret_access_key=new_payer_secret_key,
                              region_name=new_payer_region)
s3_client = boto3.client('s3',aws_access_key_id=new_payer_access_key, aws_secret_access_key=new_payer_secret_key,
                              region_name=new_payer_region)
cur_client = boto3.client('cur',aws_access_key_id=new_payer_access_key, aws_secret_access_key=new_payer_secret_key,
                              region_name='us-east-1')


params = {
    'payer_s3_name': 'bsg-billing-report-for-replication-'+new_name,
    'billing_s3_name' : 'bsg-billing-report-monitoring-'+new_name,
    'PolicyName' : 's3crr_for_bsg-billing-report-for-replication_to_bsg-billing-report-monitoring',
    'RoleName' : 's3crr_role_for_bsg-billing-report_to_bsg-billing-report-master',
    'account_id' : new_payer_account_id,
    'region' : new_payer_region,
    'report_name' : 'Billing-Report-Hourly',
    'billing_access_key' : billing_access_key,
    'billing_secret_key' : billing_secret_key

}
# print(params['new_name'])
# print(params.get('new_name'))



# 1. 정책 생성 - policies
func.create_policies(params,iam_client)
# 2. 역할 생성 - roles
func.create_role(params,iam_client)
#3. s3 버킷 생성
func.create_payer_s3_bucket(params,s3_client)
#4.비용보고서 생성
func.create_cur(params,cur_client)
# 5. billing 계정 s3 버킷 생성
func.create_billing_s3_bucket(params)
# 6. 버킷 복제 규칙
func.modify_bucket_replication_rule(params,s3_client)

