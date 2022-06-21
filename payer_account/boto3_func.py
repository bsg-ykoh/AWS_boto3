import json

import boto3

# 1. 정책 생성 - policies
def create_policies(params,iam_client):
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": [
                    "s3:Get*",
                    "s3:ListBucket"
                ],
                "Effect": "Allow",
                "Resource": [
                    f"arn:aws:s3:::{params['payer_s3_name']}",
                    f"arn:aws:s3:::{params['payer_s3_name']}/*"
                ]
            },
            {
                "Action": [
                    "s3:ReplicateObject",
                    "s3:ReplicateDelete",
                    "s3:ReplicateTags",
                    "s3:GetObjectVersionTagging",
                    "s3:ObjectOwnerOverrideToBucketOwner"
                ],
                "Effect": "Allow",
                "Resource": f"arn:aws:s3:::{params['billing_s3_name']}/*"
            }
        ]
    }

    create_policy = iam_client.create_policy(
        PolicyName=params['PolicyName'],
        PolicyDocument=json.dumps(policy_document),
        Description='billing report policy for bsgon'
    )
    print(create_policy)


# 2. 역할 생성 - roles
def create_role(params,iam_client):
    role_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "s3.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }


    create_roll = iam_client.create_role(
        RoleName=params['RoleName'],
        AssumeRolePolicyDocument=json.dumps(role_document),
        Description='billing report roll for bsgon'
    )
    print(create_roll)

    attach_role_policy = iam_client.attach_role_policy(
        RoleName= params['RoleName'],
        PolicyArn=f"arn:aws:iam::{params['account_id']}:policy/{params['PolicyName']}"
    )
    print(attach_role_policy)

# 3. s3 버킷 생성
def create_payer_s3_bucket(params,s3_client):

    policy = {
    "Version": "2008-10-17",
    "Id": "Policy1335892530063",
    "Statement": [
        {
            "Sid": "Stmt1335892150622",
            "Effect": "Allow",
            "Principal": {
                "Service": "billingreports.amazonaws.com"
            },
            "Action": [
                "s3:GetBucketAcl",
                "s3:GetBucketPolicy"
            ],
            "Resource": f"arn:aws:s3:::{params['payer_s3_name']}"
        },
        {
            "Sid": "Stmt1335892526596",
            "Effect": "Allow",
            "Principal": {
                "Service": "billingreports.amazonaws.com"
            },
            "Action": "s3:PutObject",
            "Resource": f"arn:aws:s3:::{params['payer_s3_name']}/*"
        }
    ]
}

    payer_s3_create = s3_client.create_bucket(
        ACL='private',
        Bucket=params['payer_s3_name'],
        CreateBucketConfiguration={
            'LocationConstraint': 'ap-northeast-2'
        },
        ObjectLockEnabledForBucket=False
    )
    s3_client.put_bucket_versioning(
        Bucket = params['payer_s3_name'],
        VersioningConfiguration={
            'Status': 'Enabled'
        },
    )
    s3_client.put_public_access_block(
        Bucket= params['payer_s3_name'],
        # ContentMD5='string',
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        },
        # ExpectedBucketOwner='string'
    )
    s3_client.put_bucket_policy(
        Bucket=params['payer_s3_name'],
        Policy=json.dumps(policy)
    )
    print(payer_s3_create)


# 3-1. billing 계정 s3 버킷 생성
def create_billing_s3_bucket(params):
    billing_s3_client = boto3.client('s3', aws_access_key_id=params['billing_access_key'],
                                     aws_secret_access_key= params['billing_secret_key'],
                                     region_name=params['region'])
    billing_s3_policy = {
        "Version": "2008-10-17",
        "Id": "S3-Console-Replication-Policy",
        "Statement": [
            {
                "Sid": "S3ReplicationPolicyStmt1",
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::" + params['account_id'] + ":root"
                },
                "Action": [
                    "s3:GetBucketVersioning",
                    "s3:PutBucketVersioning",
                    "s3:ReplicateObject",
                    "s3:ReplicateDelete",
                    "s3:ObjectOwnerOverrideToBucketOwner"
                ],
                "Resource": [
                    f"arn:aws:s3:::{params['billing_s3_name']}",
                    f"arn:aws:s3:::{params['billing_s3_name']}/*"
                ]
            }
        ]
    }

    billing_s3_create = billing_s3_client.create_bucket(
        Bucket=params['billing_s3_name'],
        CreateBucketConfiguration={
            'LocationConstraint': 'ap-northeast-2'
        }
    )

    billing_s3_client.put_bucket_tagging(
        Bucket=params['billing_s3_name'],
        Tagging={
            'TagSet': [
                {'Key': 'bsgon-crawl-target', 'Value': 'CUR'},
                {'Key': 'Project', 'Value': 'Billing'},
                {'Key': 'Purpose', 'Value': 'Data Lake'},
            ]
        },
    )
    billing_s3_client.put_bucket_versioning(
        Bucket=params['billing_s3_name'],
        VersioningConfiguration={
            'Status': 'Enabled'
        },
    )
    billing_s3_client.put_bucket_policy(
        Bucket=params['billing_s3_name'],
        Policy=json.dumps(billing_s3_policy)
    )
    billing_s3_client.put_public_access_block(
        Bucket=params['billing_s3_name'],
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        },
    )
    print(billing_s3_create)


# 4. 버킷 복제 규칙
def modify_bucket_replication_rule(params,s3_client):
    payer_s3_replication = s3_client.put_bucket_replication(
        Bucket=params['payer_s3_name'],
        ReplicationConfiguration={
            'Role': 'arn:aws:iam::' + params['account_id'] + ':role/' + params['RoleName'],
            # 'Role': f"arn:aws:iam::451588015814:role/{params['RoleName']}",
            'Rules': [
                {
                    'ID': 'bsg-billing-report-monitoring-policy',
                    'Status': 'Enabled',
                    'Prefix': '',

                    # 'ExistingObjectReplication': {
                    #     'Status': 'Enabled'
                    # },
                    'Destination': {
                        'Bucket': f"arn:aws:s3:::{params['billing_s3_name']}",
                        'Account': '946019410907',
                        'AccessControlTranslation': {
                            'Owner': 'Destination'
                        },

                    },

                },
            ]

        },
    )

# 5. 비용보고서 생성
def create_cur(params,cur_client):
    response = cur_client.put_report_definition(
        ReportDefinition={
            'ReportName': params['report_name'],
            'TimeUnit': 'HOURLY',
            'Format': 'textORcsv',
            'Compression': 'GZIP',
            'AdditionalSchemaElements': [
                'RESOURCES',
            ],
            'S3Bucket': params['payer_s3_name'],
            # 'S3Bucket': 'test',
            'S3Prefix': 'monitoring/',
            'S3Region': params['region'],
            'RefreshClosedReports': True,
            'ReportVersioning': 'CREATE_NEW_REPORT',
            # 'BillingViewArn': 'string'
        }
    )