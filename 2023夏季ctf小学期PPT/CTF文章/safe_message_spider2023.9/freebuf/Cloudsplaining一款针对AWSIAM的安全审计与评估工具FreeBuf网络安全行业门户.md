![](https://image.3001.net/images/20200807/1596789819.jpg!small)

## Cloudsplaining

Cloudsplaining是一个针对AWS IAM的安全审计与评估工具，该工具能够识别AWS
IAM策略中最小权限的违规情况，并以HTML格式生成以威胁等级优先的分析报告。在该工具的帮助下，广大研究人员可以扫描自己AWS账号中的所有部署策略，或扫描单个策略文件。

除此之外，该工具还能够帮助识别无资源限制的IAM活动，并通过对暴露AWS账号风险的IAM策略进行标记来帮助研究人员制定缓解方案，其中的风险包括：

  * 数据提取（s3:GetObject, ssm:GetParameter, secretsmanager:GetSecretValue）
  * 基础设施修改
  * 资源暴露
  * 权限提升

Cloudsplaining还可以识别AWS计算服务（例如EC2、ECS、EKS或Lambda）定义的IAM角色，因为它们可能会比用户定义的角色带来更大的安全风险。标记这些角色对于特定场景下的渗透测试人员（或攻击者）特别有用。例如，如果攻击者获得执行[
_ssm:SendComman_](https://docs.aws.amazon.com/systems-manager/latest/APIReference/API_SendCommand.html)d命令的权限，并且这里又有一个安装了SSM代理的特权EC2实例，那么攻击者就能够拿到这些EC2实例的特殊权限了。通过AWS系统管理器代理实现远程代码执行，已经是一个众所周知的提权/漏洞利用路径了，但是Cloudsplaining能够让我们识别整个过程变得更加轻松。

当然了，我们也可以自定义一个排除文件以筛选出因各种原因导致的误报结果。

实际上，我们很难根据最小权限原则一次性制定出最终的IAM策略，在Policy
Sentry发布之前，我们可以轻松找到IAM策略文档中缺乏的资源限制部分。我们可以看看下列例子，它将允许IAM主体（角色或用户）在AWS帐户中的任何s3
bucket上运行s3:PutObject：

    
    
    {
    
      "Version": "2012-10-17",
    
      "Statement": [
    
        {
    
          "Effect": "Allow",
    
          "Action": [
    
            "s3:PutObject"
    
          ],
    
          "Resource": "*"
    
        }
    
      ]
    
    }

这就存在问题了，理论上来说，我们应该根据资源ARN来进行访问限制：

    
    
    {
    
      "Version": "2012-10-17",
    
      "Statement": [
    
        {
    
          "Effect": "Allow",
    
          "Action": [
    
            "s3:GetObject"
    
          ],
    
          "Resource": "arn:aws:s3:::my-bucket/*"
    
        }
    
      ]
    
    }

如果您一直在使用AWS，那么可能有大量的IAM策略需要升级。如果您有数百个AWS帐户，每个帐户中都有几十个策略，那么我们如何通过编程确定应该修复的策略来锁定这些AWS帐户？Cloudsplaining就是你的答案！

## 工具安装

### Homebrew：

    
    
    brew tap salesforce/cloudsplaining https://github.com/salesforce/cloudsplaining
    
    brew install cloudsplaining

### Pip3：

    
    
    pip3 install --user cloudsplaining

接下来，我们就可以直接在命令行工具中使用下列命令来运行Cloudsplaining了：

    
    
    cloudsplaining --help

## 扫描整个AWS账号

### 下载账号授权数据

我们可以对一个AWS账号进行完整扫描，并生成报告。这里，我们需要调用AWS IAM的 [_get-account-authorization-details_](https://docs.aws.amazon.com/cli/latest/reference/iam/get-account-authorization-details.html)
API，它将会下载一个包含了账号所有IAM细节的JSON文件（大约每个账号100KB），其中将包含用户、组、角色、客户管理的策略和AWS管理的策略数据。

首先，你的AWS凭证必须配置能够通过命令行接口来使用。接下来，你必须拥有运行[
_iam:GetAccountAuthorizationDetails_](https://docs.aws.amazon.com/IAM/latest/APIReference/API_GetAccountAuthorizationDetails.html)的权限。下载账号授权数据后，确保你能够完成AWS的授权，然后运行下列命令：

    
    
    cloudsplaining download

如果你想使用自己的 ~/.aws/credentials文件而不使用环境变量的话，你可以指定配置文件名称：

    
    
    cloudsplaining download --profile myprofile

该命令将会在当前目录中下载一个包含了账户授权细节数据的JSON文件。

## 扫描单个策略

你还可以扫描单个策略文件来识别安全风险：

    
    
    cloudsplaining scan-policy-file --input examples/policies/explicit-actions.json

输出将包含一个查找描述和一个IAM活动列表（没有利用资源限制的）：

    
    
    Issue found: Data Exfiltration
    
    Actions: s3:GetObject
    
     
    
    Issue found: Resource Exposure
    
    Actions: ecr:DeleteRepositoryPolicy, ecr:SetRepositoryPolicy, s3:BypassGovernanceRetention, s3:DeleteAccessPointPolicy, s3:DeleteBucketPolicy, s3:ObjectOwnerOverrideToBucketOwner, s3:PutAccessPointPolicy, s3:PutAccountPublicAccessBlock, s3:PutBucketAcl, s3:PutBucketPolicy, s3:PutBucketPublicAccessBlock, s3:PutObjectAcl, s3:PutObjectVersionAcl
    
     
    
    Issue found: Unrestricted Infrastructure Modification
    
    Actions: ecr:BatchDeleteImage, ecr:CompleteLayerUpload, ecr:CreateRepository, ecr:DeleteLifecyclePolicy, ecr:DeleteRepository, ecr:DeleteRepositoryPolicy, ecr:InitiateLayerUpload, ecr:PutImage, ecr:PutImageScanningConfiguration, ecr:PutImageTagMutability, ecr:PutLifecyclePolicy, ecr:SetRepositoryPolicy, ecr:StartImageScan, ecr:StartLifecyclePolicyPreview, ecr:TagResource, ecr:UntagResource, ecr:UploadLayerPart, s3:AbortMultipartUpload, s3:BypassGovernanceRetention, s3:CreateAccessPoint, s3:CreateBucket, s3:DeleteAccessPoint, s3:DeleteAccessPointPolicy, s3:DeleteBucket, s3:DeleteBucketPolicy, s3:DeleteBucketWebsite, s3:DeleteObject, s3:DeleteObjectTagging, s3:DeleteObjectVersion, s3:DeleteObjectVersionTagging, s3:GetObject, s3:ObjectOwnerOverrideToBucketOwner, s3:PutAccelerateConfiguration, s3:PutAccessPointPolicy, s3:PutAnalyticsConfiguration, s3:PutBucketAcl, s3:PutBucketCORS, s3:PutBucketLogging, s3:PutBucketNotification, s3:PutBucketObjectLockConfiguration, s3:PutBucketPolicy, s3:PutBucketPublicAccessBlock, s3:PutBucketRequestPayment, s3:PutBucketTagging, s3:PutBucketVersioning, s3:PutBucketWebsite, s3:PutEncryptionConfiguration, s3:PutInventoryConfiguration, s3:PutLifecycleConfiguration, s3:PutMetricsConfiguration, s3:PutObject, s3:PutObjectAcl, s3:PutObjectLegalHold, s3:PutObjectRetention, s3:PutObjectTagging, s3:PutObjectVersionAcl, s3:PutObjectVersionTagging, s3:PutReplicationConfiguration, s3:ReplicateDelete, s3:ReplicateObject, s3:ReplicateTags, s3:RestoreObject, s3:UpdateJobPriority, s3:UpdateJobStatus

## Cheatsheet

    
    
    # 下载授权信息
    
    cloudsplaining download
    
    # 从指定配置文件下载
    
    cloudsplaining download --profile someprofile
    
     
    
    # 扫描授权信息
    
    cloudsplaining scan --input default.json
    
    # 使用自定义排除参数扫描授权细节
    
    cloudsplaining scan --input default.json --exclusions-file exclusions.yml
    
     
    
    # 扫描策略文件
    
    cloudsplaining scan-policy-file --input examples/policies/wildcards.json
    
    cloudsplaining scan-policy-file --input examples/policies/wildcards.json  --exclusions-file examples/example-exclusions.yml

## 项目地址

Cloudsplaining：【[ _GitHub传送门_](https://github.com/salesforce/cloudsplaining)】

## 参考资料

1、样本报告：[ _https://opensource.salesforce.com/cloudsplaining/#executive-summary_](https://opensource.salesforce.com/cloudsplaining/#executive-summary)

2、Policy Sentry：[
_https://github.com/salesforce/policy_sentry/_](https://github.com/salesforce/policy_sentry/)

