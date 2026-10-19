**s3tk是一款针对Amazon S3的安全审计套件，广大安全研究人员可以使用s3tk来对Amazon S3 Bucket进行安全测试。**

![](https://image.3001.net/images/20200108/1578491729_5e15df51c1623.jpg!small)

## 工具安装

广大研究人员可以使用pip来完成s3tk的安装：

    
    
    pip install s3tk

研究人员可以使用AWS CLI命令行工具来配置AWS凭证：

    
    
    pip install awscli
    
    aws configure

## 工具使用命令

### 安全扫描

可扫描的Bucket组件如下：

> 1、公开ACL
>
> 2、公开策略
>
> 3、屏蔽的公开访问
>
> 4、启用的登录
>
> 5、版本修改
>
> 6、默认加密
    
    
    s3tk scan

针对特定Bucket运行扫描：

    
    
    s3tk scan my-bucket my-bucket-2

支持通配符：

    
    
    s3tk scan "my-bucket*"

跳过日志和默认加密：

    
    
    s3tk scan --skip-logging --skip-versioning --skip-default-encryption

获取邮件通知（通过SNS）：

    
    
    s3tk scan --sns-topic arn:aws:sns:...

### 枚举策略

枚举Bucket策略：

    
    
    s3tk list-policy

针对特定Bucket运行扫描：

    
    
    s3tk list-policy my-bucket my-bucket-2

显示名称：

    
    
    s3tk list-policy --named

设置策略：

    
    
    s3tk set-policy my-bucket --no-object-acl

删除策略：

    
    
    s3tk delete-policy my-bucket

屏蔽公开访问：

    
    
    s3tk block-public-access my-bucket my-bucket-2

### 启用默认加密

针对所有Bucket启用默认加密：

    
    
    s3tk enable-default-encryption

仅针对特定Bucket启用：

    
    
    s3tk enable-default-encryption my-bucket my-bucket-2

### 扫描对象ACL

扫描目标Bucket中所有对象的ACL：

    
    
    s3tk scan-object-acl my-bucket

扫描特定对象：

    
    
    s3tk scan-object-acl my-bucket --only "*.pdf"

排除特定对象：

    
    
    s3tk scan-object-acl my-bucket --except "*.jpg"

### 扫描DNS

    
    
    s3tk scan-dns

### 凭证

用户凭证可以在“~/.aws/credentials”中或环境变量中设置，我们可以使用下列命令设置一个profile：

    
    
    AWS_PROFILE=your-profile s3tk

## IAM策略

下面给出的是每一条命令所需的权限，用户只需要将相应权限在下列代码中声明即可：

    
    
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "Scan",
                "Effect": "Allow",
                "Action": [
                    "s3:ListAllMyBuckets",
                    "s3:GetBucketAcl",
                    "s3:GetBucketPolicy",
                    "s3:GetBucketPublicAccessBlock",
                    "s3:GetBucketLogging",
                    "s3:GetBucketVersioning",
                    "s3:GetEncryptionConfiguration"
                ],
                "Resource": "*"
            },
            {
                "Sid": "ScanDNS",
                "Effect": "Allow",
                "Action": [
                    "s3:ListAllMyBuckets",
                    "route53:ListHostedZones",
                    "route53:ListResourceRecordSets"
                ],
                "Resource": "*"
            },
            {
                "Sid": "ListPolicy",
                "Effect": "Allow",
                "Action": [
                    "s3:ListAllMyBuckets",
                    "s3:GetBucketPolicy"
                ],
                "Resource": "*"
            },
            {
                "Sid": "SetPolicy",
                "Effect": "Allow",
                "Action": [
                    "s3:PutBucketPolicy"
                ],
                "Resource": "*"
            },
            {
                "Sid": "DeletePolicy",
                "Effect": "Allow",
                "Action": [
                    "s3:DeleteBucketPolicy"
                ],
                "Resource": "*"
            },
            {
                "Sid": "BlockPublicAccess",
                "Effect": "Allow",
                "Action": [
                    "s3:ListAllMyBuckets",
                    "s3:PutBucketPublicAccessBlock"
                ],
                "Resource": "*"
            },
            {
                "Sid": "EnableLogging",
                "Effect": "Allow",
                "Action": [
                    "s3:ListAllMyBuckets",
                    "s3:PutBucketLogging"
                ],
                "Resource": "*"
            },
            {
                "Sid": "EnableVersioning",
                "Effect": "Allow",
                "Action": [
                    "s3:ListAllMyBuckets",
                    "s3:PutBucketVersioning"
                ],
                "Resource": "*"
            },
            {
                "Sid": "EnableDefaultEncryption",
                "Effect": "Allow",
                "Action": [
                    "s3:ListAllMyBuckets",
                    "s3:PutEncryptionConfiguration"
                ],
                "Resource": "*"
            },
            {
                "Sid": "ResetObjectAcl",
                "Effect": "Allow",
                "Action": [
                    "s3:ListBucket",
                    "s3:GetObjectAcl",
                    "s3:PutObjectAcl"
                ],
                "Resource": [
                    "arn:aws:s3:::my-bucket",
                    "arn:aws:s3:::my-bucket/*"
                ]
            },
            {
                "Sid": "Encrypt",
                "Effect": "Allow",
                "Action": [
                    "s3:ListBucket",
                    "s3:GetObject",
                    "s3:PutObject"
                ],
                "Resource": [
                    "arn:aws:s3:::my-bucket",
                    "arn:aws:s3:::my-bucket/*"
                ]
            },
            {
                "Sid": "DeleteUnencryptedVersions",
                "Effect": "Allow",
                "Action": [
                    "s3:ListBucketVersions",
                    "s3:GetObjectVersion",
                    "s3:DeleteObjectVersion"
                ],
                "Resource": [
                    "arn:aws:s3:::my-bucket",
                    "arn:aws:s3:::my-bucket/*"
                ]
            }
        ]
    }

## 访问日志

Amazon Athena适用于查询S3日志，创建下列表：

    
    
    CREATE EXTERNAL TABLE my_bucket (
        bucket_owner string,
        bucket string,
        time string,
        remote_ip string,
        requester string,
        request_id string,
        operation string,
        key string,
        request_verb string,
        request_url string,
        request_proto string,
        status_code string,
        error_code string,
        bytes_sent string,
        object_size string,
        total_time string,
        turn_around_time string,
        referrer string,
        user_agent string,
        version_id string
    )
    ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.RegexSerDe'
    WITH SERDEPROPERTIES (
        'serialization.format' = '1',
        'input.regex' = '([^ ]*) ([^ ]*) \\[(.*?)\\] ([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*) \\\"([^ ]*) ([^ ]*) (- |[^ ]*)\\\" (-|[0-9]*) ([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*) (\"[^\"]*\\") ([^ ]*)$'
    ) LOCATION 's3://my-s3-logs/my-bucket/';

修改最后一行代码，并指向你的日志Bucket：

    
    
    SELECT
        date_parse(time, '%d/%b/%Y:%H:%i:%S +0000') AS time,
        request_url,
        remote_ip,
        user_agent
    FROM
        my_bucket
    WHERE
        requester = '-'
        AND status_code LIKE '2%'
        AND request_url LIKE '/some-keys%'
    ORDER BY 1

## CloudTrail日志

Amazon Athena同样可以用于查询CloudTrail日志，创建一个表：

    
    
    CREATE EXTERNAL TABLE cloudtrail_logs (
        eventversion STRING,
        userIdentity STRUCT<
            type:STRING,
            principalid:STRING,
            arn:STRING,
            accountid:STRING,
            invokedby:STRING,
            accesskeyid:STRING,
            userName:String,
            sessioncontext:STRUCT<
                attributes:STRUCT<
                    mfaauthenticated:STRING,
                    creationdate:STRING>,
                sessionIssuer:STRUCT<
                    type:STRING,
                    principalId:STRING,
                    arn:STRING,
                    accountId:STRING,
                    userName:STRING>>>,
        eventTime STRING,
        eventSource STRING,
        eventName STRING,
        awsRegion STRING,
        sourceIpAddress STRING,
        userAgent STRING,
        errorCode STRING,
        errorMessage STRING,
        requestId  STRING,
        eventId  STRING,
        resources ARRAY<STRUCT<
            ARN:STRING,
            accountId:STRING,
            type:STRING>>,
        eventType STRING,
        apiVersion  STRING,
        readOnly BOOLEAN,
        recipientAccountId STRING,
        sharedEventID STRING,
        vpcEndpointId STRING,
        requestParameters STRING,
        responseElements STRING,
        additionalEventData STRING,
        serviceEventDetails STRING
    )
    ROW FORMAT SERDE 'com.amazon.emr.hive.serde.CloudTrailSerde'
    STORED  AS INPUTFORMAT 'com.amazon.emr.cloudtrail.CloudTrailInputFormat'
    OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
    LOCATION  's3://my-cloudtrail-logs/'

修改最后一行代码，并指向你的CloudTrail日志Bucket：

    
    
    SELECT
        eventTime,
        eventName,
        userIdentity.userName,
        requestParameters
    FROM
        cloudtrail_logs
    WHERE
        eventName LIKE '%Bucket%'
    ORDER BY 1

## Bucket策略

    
    
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Deny",
                "Principal": "*",
                "Action": "s3:PutObjectAcl",
                "Resource": "arn:aws:s3:::my-bucket/*"
            }
        ]
    }

## 工具更新

运行下列命令：

    
    
    pip install s3tk --upgrade

使用Master，可运行下列命令：

    
    
    pip install git+https://github.com/ankane/s3tk.git --upgrade

## Docker运行

运行下列命令：

    
    
    docker run -it ankane/s3tk aws configure

提交你的凭证：

    
    
    docker commit $(docker ps -l -q) my-s3tk

接下来，运行下列命令：

    
    
    docker run -it my-s3tk s3tk scan

### 工具运行截图

![](https://image.3001.net/images/20200108/1578491953_5e15e031ba172.gif!small)

## 项目地址

> s3tk：【[ _GitHub传送门_](https://github.com/ankane/s3tk)】

 *** 参考来源：[
_ankane_](https://github.com/ankane/s3tk)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

