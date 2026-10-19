![](https://image.3001.net/images/20221018/1666101196_634eafcc66639c462b799.jpg!small)

## 关于CloudFox

CloudFox是一款针对云环境渗透测试的自动化安全态势感知工具，该工具可以帮助广大研究人员以自动化的形式在自己并不熟悉的云环境中获得环境安全态势感知。该工具是一个开源的命令行工具，旨在帮助渗透测试人员和红队安全专业人员在云基础设施中找到可利用的攻击路径，并以此来提升云端环境的安全性。

## CloudFox功能介绍

> 1、查看AWS账户使用的是哪个地区，账户中大致有多少资源；
>
> 2、查看EC2用户数据或特定于服务的环境变量；
>
> 3、查看目标主体可执行的操作和拥有的权限；
>
> 4、查看哪些角色授信过于宽松或允许跨账户操作；
>
> 5、获取从外部起点（公共互联网）可以攻击哪些端点/主机名/IP；
>
> 6、获取从内部起点攻击哪些端点/主机名/IP（假设VPC内出现漏洞）；
>
> 7、查看可以从VPC内的受损资源中装载哪些文件系统；

## 支持的云服务商

 ** **云服务提供商****

|

 ** **CloudFox**** ** **命令****  
  
---|---  
  
AWS

|

15  
  
Azure

|

2 (测试中)  
  
GCP

|

即将支持  
  
Kubernetes

|

即将支持  
  
## 工具安装

### Releases版本

广大研究人员可以直接访问该项目的【[
_Releases页面_](https://github.com/BishopFox/cloudfox/releases)】下载最新版本的工具源码。

### 源码安装

该工具基于Golang开发，因此我们首先需要在本地设备上安装并配置好[
_Go_](https://golang.org/doc/install)环境。接下来，使用下列命令将该项目源码克隆至本地，并编译工具源码：

    
    
    # git clone https://github.com/BishopFox/cloudfox.git
    
    ...omitted for brevity...
    
    # cd ./cloudfox
    
    # go build .
    
    # ./cloudfox

### 辅助工具

 **AWS CLI** ：【[
_点我安装_](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)】

 **Azure CLI** ：【[ _点我安装_](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)】

## 工具使用

### AWS使用

CloudFox是一款模块化的工具，我们可以每次只运行一个命令，其中的all-checks命令是一个AWS命令，它将会运行其他AWS命令：

    
    
    cloudfox aws --profile [profile-name] all-checks

配置AWS API密钥：

    
    
    # aws configure --profile readonly
    
    AWS Access Key ID [None]: AKIA-[REDACTED]
    
    AWS Secret Access Key [None]: c9gnnAG-[REDACTED]
    
    Default region name [None]: us-east-1
    
    Default output format [None]: json

查看所有可用的AWS命令：

    
    
    # ./cloudfox aws -h

查看命令帮助信息

    
    
    ./cloudfox aws [command_name] -h

### Azure使用

客户端认证：

    
    
    # az login
    
    To sign in, use a web browser to open the page https://microsoft.com/devicelogin and enter the code [REDACTED] to authenticate.
    
    [
    
      {
    
        "cloudName": "AzureCloud",
    
        "homeTenantId": "[REDACTED]",
    
        "id": "[REDACTED]",
    
        "isDefault": true,
    
        "managedByTenants": [],
    
        "name": "[REDACTED]",
    
        "state": "Enabled",
    
        "tenantId": "[REDACTED]",
    
        "user": {
    
          "name": "[REDACTED]",
    
          "type": "user"
    
        }
    
      },
    
    ...omitted for brevity...

查看可用的Azure命令：

    
    
    # ./cloudfox azure -h

查看命令帮助信息：

    
    
    ./cloudfox azure [command_name] -h

## 工具使用演示

### AWS-运行所有的检测命令

    
    
    ./cloudfox aws --profile cf-exec all-checks
    [cloudfox] AWS Caller Identity: arn:aws:iam::049881439828:user/terraform-user
    [cloudfox] Getting a lay of the land, aka "What regions is this account using?"
    [inventory] Enumerating selected services in all regions for account 049881439828.
    [inventory] Supported Services: ApiGateway, ApiGatewayv2, AppRunner, CloudFormation, Cloudfront, EC2, EKS,
    [inventory]    ELB, ELBv2, Grafana, IAM, Lambda, Lightsail, MQ, OpenSearch, RDS, S3, SecretsManager, SSM
    [inventory] Status: 336/336 tasks complete (86 errors -- For details check /Users/sethart/.cloudfox/cloudfox-error.log)
    [inventory] Output written to [cloudfox-output/aws/cf-prod/table/inventory.txt]
    [inventory-global] Output written to [cloudfox-output/aws/cf-prod/table/inventory-global.txt]
    [inventory] 68 resources enumerated in the services we looked at. This is NOT the total number of resources in the account.
    [cloudfox]Gathering the info you'll want for your application & service enumeration needs.
    [instances] Enumerating EC2 instances in all regions for account 049881439828
    [instances] Status: 21/21 tasks complete (4 errors -- For details check /Users/sethart/.cloudfox/cloudfox-error.log)
    [instances] Output written to [cloudfox-output/aws/cf-prod/table/instances.txt]
    [instances] Loot written to [cloudfox-output/aws/cf-prod/loot/instances-ec2PrivateIPs.txt]
    [instances] Loot written to [cloudfox-output/aws/cf-prod/loot/instances-ec2PublicIPs.txt]
    [instances] 7 instances found.
    [route53] Enumerating Route53 for account 049881439828.
    [route53] No DNS records found, skipping the creation of an output file.
    [filesystems] Enumerating filesystems for account 049881439828.
    [filesystems] Supported Services: EFS, FSx
    [filesystems] Status: 0/0 tasks complete (0 errors -- For details check /Users/sethart/.cloudfox/cloudfox-error.log)
    [filesystems] No filesystems found, skipping the creation of an output file.
    [endpoints] Enumerating endpoints for account 049881439828.
    [endpoints] Supported Services: App Runner, APIGateway, ApiGatewayV2, Cloudfront, EKS, ELB, ELBv2, Grafana,
    [endpoints]    Lambda, MQ, OpenSearch, Redshift, RDS
    [endpoints] Status: 274/274 tasks complete (68 errors -- For details check /Users/sethart/.cloudfox/cloudfox-error.log)
    [endpoints] Output written to [cloudfox-output/aws/cf-prod/table/endpoints.txt]
    [endpoints] Loot written to [cloudfox-output/aws/cf-prod/loot/endpoints-UrlsOnly.txt]
    [endpoints] 5 endpoints enumerated.
    [cloudfox] Looking for secrets hidden between the seat cushions.
    [instances] Enumerating EC2 instances in all regions for account 049881439828
    [instances] Status: 21/21 tasks complete (4 errors -- For details check /Users/sethart/.cloudfox/cloudfox-error.log)
    [instance-userdata] Loot written to [cloudfox-output/aws/cf-prod/loot/instance-userdata.txt]
    [env-vars] Enumerating environment variables in all regions for account 049881439828.
    [env-vars] Supported Services: App Runner, Elastic Container Service, Lambda, Lightsail Containers, Sagemaker
    [env-vars] Status: 105/105 tasks complete (48 errors -- For details check /Users/sethart/.cloudfox/cloudfox-error.log)
    [env-vars] Output written to [cloudfox-output/aws/cf-prod/table/env-vars.txt]
    [env-vars] 5 environment variables found.
    [cloudfox] Arming you with the data you'll need for privesc quests.
    [buckets] Enumerating buckets for account 049881439828.
    [buckets] Status: 1/1 tasks complete (0 errors -- For details check /Users/sethart/.cloudfox/cloudfox-error.log)
    [buckets] Output written to [cloudfox-output/aws/cf-prod/table/buckets.txt]
    [buckets] Loot written to [cloudfox-output/aws/cf-prod/loot/bucket-commands.txt]
    [buckets] 3 buckets found.
    [ecr] Enumerating container repositories for account 049881439828.
    [ecr] Status: 21/21 regions complete (4 errors -- For details check /Users/sethart/.cloudfox/cloudfox-error.log)
    [ecr] No repositories found, skipping the creation of an output file.
    [secrets] Enumerating secrets for account 049881439828.
    [secrets] Supported Services: SecretsManager, SSM Parameters
    [secrets] Status: 21/21 regions complete (8 errors -- For details check /Users/sethart/.cloudfox/cloudfox-error.log)
    [secrets] Output written to [cloudfox-output/aws/cf-prod/table/secrets.txt]
    [secrets] 7 secrets found.
    [cloudfox] IAM is complicated. Complicated usually means misconfigurations. You'll want to pay attention here.
    [principals] Enumerating IAM Users and Roles for account 049881439828.
    [principals] Output written to [cloudfox-output/aws/cf-prod/table/principals.txt]
    [principals] 36 IAM principals found.
    [permissions] Enumerating IAM permissions for account 049881439828.
    [permissions] Output written to [cloudfox-output/aws/cf-prod/table/permissions.txt]
    [permissions] 3058 unique permissions identified.
    [access-keys] Mapping user access keys for account: 049881439828.
    [access-keys] Only active access keys are shown.
    [access-keys] Output written to [cloudfox-output/aws/cf-prod/table/access-keys.txt]
    [access-keys] Loot written to [cloudfox-output/aws/cf-prod/loot/access-keys.txt]
    [access-keys] 5 access keys found.
    [role-trusts] Enumerating role trusts for account 049881439828.
    [role-trusts-principals] Output written to [cloudfox-output/aws/cf-prod/table/role-trusts-principals.txt]
    [role-trusts-principals] 9 role trusts found.
    [role-trusts-services] Output written to [cloudfox-output/aws/cf-prod/table/role-trusts-services.txt]
    [role-trusts-services] 19 role trusts found.
    [iam-simulator] Running multiple iam-simulator queries for account 049881439828. (This command can be pretty slow, FYI)
    [iam-simulator] Status: 2/2 tasks complete (0 errors -- For details check /Users/sethart/.cloudfox/cloudfox-error.log)
    [iam-simulator] Output written to [cloudfox-output/aws/cf-prod/table/iam-simulator.txt]
    [iam-simulator] We suggest running the pmapper commands in the loot file to get the same information but taking privesc paths into account.
    [iam-simulator] Loot written to [cloudfox-output/aws/cf-prod/loot/iam-simulator-pmapper-commands.txt]
    [cloudfox] That's it! Check your output files for situational awareness and check your loot files for next steps.
    [cloudfox] FYI, we skipped the outbound-assumed-roles command in all-checks (really long run time). Make sure to try it out manually.

### Azure-枚举关于目标用户所有资源组计算实例的全部信息

    
    
    # ./cloudfox azure instances-map --output table                                      
    
    [*] Enumerating compute instances for all subscriptions...
    
    [*] aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa... done!
    
    [*] bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbbb... done!
    
     
    
    [*] Preparing output...
    
     
    
     RESOURCE_GROUP   NAME      OS                              ADMIN_USERNAME   INTERNAL_IPS          EXTERNAL_IPS                    
    
    ---------------- --------- ------------------------------- ---------------- --------------------- ---------------------------------    
     Test1            TestVM1   WindowsServer 2019-Datacenter   adminuser        [10.0.1.5 10.0.1.7]   [20.106.248.146 20.106.248.183]
    
     Test1            TestVM2   WindowsServer 2019-Datacenter   adminuser        [10.0.1.4]            [20.106.248.25]                 
    
     Test2            TestVM3   WindowsServer 2019-Datacenter   adminuser        [10.0.1.6]            [13.64.170.251]   

### Azure-枚举所有的角色信息

    
    
    # ./cloudfox azure rbac-map
    
    [*] Entering tenant: 1111111111-1111-1111-1111-111111111111
    
    [*] Enumerating 2 users...
    
    [*] Done!
    
    [*] Enumerating 322 roles in subscription aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa...
    
    [*] Enumerating 322 roles in subscription bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbbb...
    
    [*] Done!
    
    [*] Enumerating 3 role assignments in subscription aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa...
    
    [*] Enumerating 1 role assignments in subscription bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbbb...
    
    [*] Done!
    
     
    
     PRINCIPAL_NAME      PRINCIPAL_ID                           PRINCIPAL_TYPE   ROLE_NAME     SCOPE_LEVEL      SCOPE_NAME                           
    
    ------------------- -------------------------------------- ---------------- ------------- ---------------- --------------------------------------    
     Carlos Vendramini   73d5b926-b258-47a2-891c-b14bf9da5dde   User             Owner         subscriptions    aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa
    
     None                00472a46-e07f-43af-a9a0-c1576171e83d   Other            Contributor   subscriptions    aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa
    
     Example User        6d1df2ce-44e2-4a84-b22a-4755d1fcbd65   User             Reader        resourceGroups   NetworkWatcherRG                     
    
     Carlos Vendramini   73d5b926-b258-47a2-891c-b14bf9da5dde   User             Owner         subscriptions    bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbbb

### Azure-枚举指定用户分配的全部角色

    
    
    # ./cloudfox azure rbac-map --user "Example User" --output csv
    
    [*] Entering tenant: 1111111111-1111-1111-1111-111111111111
    
    [*] Enumerating 2 users...
    
    [*] Done!
    
    [*] Enumerating 322 roles in subscription aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa...
    
    [*] Enumerating 322 roles in subscription bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbbb...
    
    [*] Done!
    
    [*] Enumerating 3 role assignments in subscription aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa...
    
    [*] Enumerating 1 role assignments in subscription bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbbb...
    
    [*] Done!
    
     
    
    PRINCIPAL_NAME, PRINCIPAL_ID, PRINCIPAL_TYPE, ROLE_NAME, SCOPE_LEVEL, SCOPE_NAME
    
    Example User, 6d1df2ce-44e2-4a84-b22a-4755d1fcbd65, User, Reader, resourceGroups, NetworkWatcherRG

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/BishopFox/cloudfox/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **CloudFox** ：【[ _GitHub传送门_](https://github.com/BishopFox/cloudfox)】

## 参考资料

> [ _https://golang.org/doc/install_](https://golang.org/doc/install)
>
> [
> _https://github.com/BishopFox/smogcloud_](https://github.com/BishopFox/smogcloud)
>
> [
> _https://github.com/SummitRoute/aws_exposable_resources_](https://github.com/SummitRoute/aws_exposable_resources)
>
> [ _https://steampipe.io/_](https://steampipe.io/)
>
> [
> _https://github.com/nccgroup/PMapper_](https://github.com/nccgroup/PMapper)
>
> [
> _https://github.com/salesforce/cloudsplaining_](https://github.com/salesforce/cloudsplaining)
>
> [
> _https://github.com/nccgroup/ScoutSuite_](https://github.com/nccgroup/ScoutSuite)
>
> [ _https://github.com/prowler-cloud/prowler_](https://github.com/prowler-> cloud/prowler)
>
> [
> _https://github.com/RhinoSecurityLabs/pacu_](https://github.com/RhinoSecurityLabs/pacu)
>
> [ _https://github.com/duo-labs/cloudmapper_](https://github.com/duo-> labs/cloudmapper)

