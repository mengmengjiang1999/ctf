![](https://image.3001.net/images/20211122/1637588763_619b9f1bd653618633f52.jpg!small)

## 关于Domain-Protect

Domain-Protect是一款功能强大的子域名安全保护工具，可以帮助广大研究人员更好地保护自己的网站抵御子域名接管攻击。该工具支持实现以下两个目标：

  * 扫描一个AWS组织中的Amazon Route53，并获取存在安全问题的域名记录，然后尝试执行域名接管检测；
  * 可以通过[ _Domain Protect for GCP_](https://github.com/ovotech/domain-protect-gcp)检测Google Cloud DNS中存在安全问题的域名；

## 子域名检测功能

扫描Amazon Route53以识别：

  * 缺少S3源的CloudFront发行版的ALIAS记录；
  * 缺少S3源的CloudFront发行版的CNAME记录；
  * 存在接管漏洞的ElasticBeanstalk的ALIAS记录；
  * 缺少托管区域的已注册域名；
  * 易被接管的子域名；
  * 易被接管的S3ALIAS记录；
  * 易被接管的S3CNAME记录；
  * Azure资源中存在安全问题的CNAME记录；
  * 缺少Google云存储Bucket的CNAME记录；

## 可选的额外检测

这些额外的检测功能默认是关闭的，因为可能在扫描大型组织时会导致Lambda超时，比如说扫描缺少Google云存储Bucket的A记录。如需启用，请在你的tfvars文件或CI/CD管道中
创建下列Terraform变量：

    
    
    lambdas = ["alias-cloudfront-s3", "alias-eb", "alias-s3", "cname-cloudfront-s3", "cname-eb", "cname-s3", "ns-domain", "ns-subdomain", "cname-azure", "cname-google", "a-storage"]

## 通知

  * 针对扫描到的每种漏洞类型通过Slack通知 ，枚举出账号名称和漏洞域名；
  * 订阅SNS主题，发送JSON格式的电子邮件通知，其中包含帐户名、帐户ID和存在安全问题的域名；

## 工具要求

  * 需要AWS组织内的安全审计账号；
  * 在组织中的每个AWS帐户都具有相同名称的安全审核只读角色；
  * 针对Terraform状态文件的Storage Bucket；
  * Terraform 1.0.x；

## 工具源码获取

广大研究人员可以通过下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/ovotech/domain-protect.git

## 工具使用

  * 以下列命令形式替换Terraform状态S3 Bucket字段（TERRAFORM_STATE_BUCKET）；
  * 针对本地测试，拷贝项目中的tfvars.example，重命名并去掉.example后缀；
  * 输入你组织相关的详情信息；
  * 在你的CI/CD管道中输出Terraform变量；

## AWS IAM策略

针对最小特权访问控制，项目提供了AWS IAM策略样例：

  * [ _domain-protect audit policy_](https://github.com/ovotech/domain-protect/blob/dev/aws-iam-policies/domain-protect-audit.json)
  * [ _domain-protect audit trust relationship_](https://github.com/ovotech/domain-protect/blob/dev/aws-iam-policies/domain-protect-audit-trust.json)
  * [ _domain-protect audit trust relationship with External ID_](https://github.com/ovotech/domain-protect/blob/dev/aws-iam-policies/domain-protect-audit-trust-external-id.json)
  * [ _domain-protect deploy policy_](https://github.com/ovotech/domain-protect/blob/dev/aws-iam-policies/domain-protect-deploy.json)

## 工具使用截图

### 部署至安全审计账号

![](https://image.3001.net/images/20211122/1637588825_619b9f596be6a45f90366.png!small)

### 扫描整个AWS组织

![](https://image.3001.net/images/20211122/1637588831_619b9f5fd16a631c06ea6.png!small)

### 通过Slack或电子邮件接收提醒消息

![](https://image.3001.net/images/20211122/1637588837_619b9f65d5dc174add8cc.png!small)

### 通过笔记本电脑手动执行扫描任务

![](https://image.3001.net/images/20211122/1637588846_619b9f6eaf76edcfc082a.png!small)

## 项目地址

 **Domain-Protect：** 【[ _GitHub传送门_](https://github.com/ovotech/domain-protect)】

## 参考资料

  * [ _https://github.com/ovotech/domain-protect-gcp_](https://github.com/ovotech/domain-protect-gcp)
  * [ _https://github.com/ovotech/domain-protect/blob/dev/manual-scans/README.md_](https://github.com/ovotech/domain-protect/blob/dev/manual-scans/README.md)
  * [ _https://github.com/ovotech/domain-protect/blob/dev/variables.tf_](https://github.com/ovotech/domain-protect/blob/dev/variables.tf)
  * [ _https://github.com/ovotech/domain-protect/blob/dev/aws-iam-policies/domain-protect-deploy.json_](https://github.com/ovotech/domain-protect/blob/dev/aws-iam-policies/domain-protect-deploy.json)

