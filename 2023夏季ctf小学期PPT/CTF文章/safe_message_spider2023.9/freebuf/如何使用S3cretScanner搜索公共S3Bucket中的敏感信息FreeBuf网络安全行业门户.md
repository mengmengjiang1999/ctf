![](https://image.3001.net/images/20221225/1671970007_63a83cd7e55c798e2b850.png!small)

## 关于S3cret Scanner

S3cret Scanner是一款针对S3 Bucket的安全扫描工具，在该工具的帮助下，广大研究人员可以轻松扫描上传到公共S3 Bucket中的敏感信息。

S3cret Scanner工具旨在为[ _Amazon
S3安全最佳实践_](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)提供一个补充层，该工具可以通过主动搜索模式来搜索公共S3
Bucket中的敏感数据。值得一提的是，该工具支持通过计划任务执行或手动按需执行。

## 自动化工作流

该工具的自动化工作流将会自动执行下列操作：

> 1、枚举目标账号中的公共Bucket（ACL设置为了Public或objects can be public）；
>
> 2、枚举敏感文本数据或敏感文件（例如.p12或.pgp等）；
>
> 3、可以从目标磁盘中下载、扫描（使用truffleHog3）和删除文件，评估完成后，再逐个删除文件；
>
> 4、支持在logger.log文件中存储日志信息；

## 工具要求

1、Python 3.6 +

2、TruffleHog3（并在$PATH中设置好环境变量）；

3、一个包含下列权限的AWS角色：

    
    
    {
    
        "Version": "2012-10-17",
    
        "Statement": [
    
            {
    
                "Sid": "VisualEditor0",
    
                "Effect": "Allow",
    
                "Action": [
    
                    "s3:GetLifecycleConfiguration",
    
                    "s3:GetBucketTagging",
    
                    "s3:ListBucket",
    
                    "s3:GetAccelerateConfiguration",
    
                    "s3:GetBucketPolicy",
    
                    "s3:GetBucketPublicAccessBlock",
    
                    "s3:GetBucketPolicyStatus",
    
                    "s3:GetBucketAcl",
    
                    "s3:GetBucketLocation"
    
                ],
    
                "Resource": "arn:aws:s3:::*"
    
            },
    
            {
    
                "Sid": "VisualEditor1",
    
                "Effect": "Allow",
    
                "Action": "s3:ListAllMyBuckets",
    
                "Resource": "*"
    
            }
    
        ]
    
    }

4、如果你使用了一个CSV文件，请确保csv目录中存储了这个csv文件（accounts.csv），文件格式如下：

    
    
    Account name,Account id
    
    prod,123456789
    
    ci,321654987
    
    dev,148739578

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Eilonh/s3crets_scanner.git

接下来，使用pip3和项目提供的requirements.txt安装该工具所需的依赖组件（包括TruffleHog3）：

    
    
    pip3 install -r requirements.txt
    
    pip3 install trufflehog3

## 工具使用

 ** **命令参数****

|

 ** **可选值****

|

 ** **参数描述****

|

 ** **是否必须****  
  
---|---|---|---  
  
-p, --aws_profile

|

  

|

访问密钥的AWS账号名称

|

✓  
  
-r, --scanner_role

|

  

|

AWS扫描器的角色名称

|

✓  
  
-m, --method

|

internal

|

扫描类型

|

✓  
  
-l, --last_modified

|

1-365

|

自动文件上一次被修改后的扫描天数; 默认为- 1

|

✗  
  
## 工具使用样例

    
    
    python3 main.py -p secTeam -r secteam-inspect-s3-buckets -l 1

## 工具使用演示

![](https://image.3001.net/images/20221225/1671970231_63a83db785f791787b809.gif!small)

## 许可证协议

本项目的开发与发布遵循[ _Apache_
_2.0_](https://opensource.org/licenses/Apache-2.0)开源许可证协议。

## 项目地址

 **S3cret Scanner** ：【[
_GitHub传送门_](https://github.com/Eilonh/s3crets_scanner)】

## 参考资料

> [ _https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-> practices.html_](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-> best-practices.html)
>
> [ _https://medium.com/@hareleilon/hunting-after-secrets-accidentally-> uploaded-to-> public-s3-buckets-7e5bbbb80097_](https://medium.com/@hareleilon/hunting-> after-secrets-accidentally-uploaded-to-public-s3-buckets-7e5bbbb80097)

