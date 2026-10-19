## 关于Ghostbuster

Ghostbuster是一款功能强大的Elastic安全审计工具，该工具可以通过对目标AWS账号中的资源进行分析，从而消除Elastic悬空IP。

Ghostbuster可以帮助广大研究人员获取目标AWS账号（Route53）中所有的DNS记录，并能够选择通过CSV输入或Cloudflare来接收搜索到的记录。

收集到这些记录和数据之后，Ghostbuster将会遍历所有AWS Elastic IP和网络接口公共IP，并收集这些数据。

在拿到所有DNS记录（来自route53、文件输入或cloudflare）的完整信息，以及目标组织拥有的AWS
IP的完整信息之后，该工具将能够检测出指向悬空Elastic IP（已失效）的子域名了。

## 功能介绍

> 1、动态枚举“.aws/config”中的每一个AWS账号；
>
> 2、从AWS Route53中提取记录；
>
> 3、从Cloudflare中提取记录（可选）；
>
> 4、从CSV输入中提取记录（可选）；
>
> 5、遍历所有区域、单个区域或以逗号分隔的区域列表；
>
> 6、获取与所有AWS帐户关联的所有Elastic IP；
>
> 7、获取与所有AWS帐户关联的所有公共IP；
>
> 8、交叉检查DNS记录，以及组织拥有的IP，以检测潜在的接管风险；
>
> 9、Slack Webhook支持发送接管通知；

## 工具下载&安装

该工具基于Python开发，因此我们首先需要在本地设备上安装并配置好Python 3.x环境。

Ghostbuster的下载和安装都非常简单，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/assetnote/ghostbuster.git

或者直接使用下列命令进行安装：

    
    
    pip install ghostbuster

然后通过“ghostbuster”命令来使用Ghostbuster即可。

## 工具使用

    
    
    ❯ ghostbuster scan aws --help                                                                                                                                                                     
    
    Usage: ghostbuster scan aws [OPTIONS]
    
     
    
      Scan for dangling elastic IPs inside your AWS accounts.
    
     
    
    Options:
    
      --profile TEXT           指定Ghostbuster需要扫描的AWS账号信息
    
     
    
      --skipascii              Ghostbuster启动之后，不打印ASCII字符
    
     
    
      --slackwebhook TEXT    指定一个Slack Webhook URL以发送潜在接管的通知信息 
    
     
    
      --records PATH          手动指定要检查的DNS记录。Ghostbuster将在检查检索到的DNS记录后检查这些IP
    
     
    
      --cloudflaretoken TEXT   从Cloudflare中提取DNS记录，需提供CF API令牌
    
     
    
      --allregions              扫描全范围
    
      --exclude TEXT          要排除的配置文件名称列表，用逗号分隔
    
      --regions TEXT           要扫描的区域列表，用逗号分隔
    
      --help                  显示帮助信息和退出

## 配置Cloudflare

![](https://image.3001.net/images/20220325/1648188980_623d5e3467791be4b3573.png!small)

## 配置AWS账号

 **.aws/credentials:**

    
    
    [default]
    
    aws_access_key_id = AKIAIII...
    
    aws_secret_access_key = faAaAaA...

 **.aws/config:**

    
    
    [default]
    
    output = table
    
    region = us-east-1
    
     
    
    [profile account-one]
    
    role_arn = arn:aws:iam::911111111113:role/Ec2Route53Access
    
    source_profile = default
    
    region = us-east-1
    
     
    
    [profile account-two]
    
    role_arn = arn:aws:iam::911111111112:role/Ec2Route53Access
    
    source_profile = default
    
    region = us-east-1
    
     
    
    [profile account-three]
    
    region = us-east-1
    
    role_arn = arn:aws:iam::911111111111:role/Ec2Route53Access
    
    source_profile = default

## 工具使用样例

运行Ghostbuster，提供Cloudflare DNS记录的访问令牌，向Slack
Webhook发送通知，遍历的所有AWS区域中“.aws/config or .aws/credentials”内配置的每一个AWS账号：

    
    
    ❯ ghostbuster scan aws --cloudflaretoken APIKEY --slackwebhook https://hooks.slack.com/services/KEY --allregions

使用手动输入的子域名A记录列表（具体可参考records.csv格式）运行Ghostbuster：

    
    
    ❯ ghostbuster scan aws --records records.csv

## 工具输出样例

    
    
    ❯ ghostbuster scan aws --cloudflaretoken whougonnacall
    
    Obtaining all zone names from Cloudflare.
    
    Obtaining DNS A records for all zones from Cloudflare.
    
    Obtained 33 DNS A records so far.
    
    Obtaining Route53 hosted zones for AWS profile: default.
    
    Obtaining Route53 hosted zones for AWS profile: account-five.
    
    Obtaining Route53 hosted zones for AWS profile: account-four.
    
    Obtaining Route53 hosted zones for AWS profile: account-four-deploy.
    
    Obtaining Route53 hosted zones for AWS profile: account-two-deploy.
    
    Obtaining Route53 hosted zones for AWS profile: account-one-deploy.
    
    Obtaining Route53 hosted zones for AWS profile: account-three-deploy.
    
    Obtaining Route53 hosted zones for AWS profile: account-six.
    
    Obtaining Route53 hosted zones for AWS profile: account-seven.
    
    Obtaining Route53 hosted zones for AWS profile: account-one.
    
    Obtained 124 DNS A records so far.
    
    Obtaining EIPs for region: us-east-1, profile: default
    
    Obtaining IPs for network interfaces for region: us-east-1, profile: default
    
    Obtaining EIPs for region: us-east-1, profile: account-five
    
    Obtaining IPs for network interfaces for region: us-east-1, profile: account-five
    
    Obtaining EIPs for region: us-east-1, profile: account-four
    
    Obtaining IPs for network interfaces for region: us-east-1, profile: account-four
    
    Obtaining EIPs for region: us-east-1, profile: account-four-deploy
    
    Obtaining IPs for network interfaces for region: us-east-1, profile: account-four-deploy
    
    Obtaining EIPs for region: us-east-1, profile: account-two-deploy
    
    Obtaining IPs for network interfaces for region: us-east-1, profile: account-two-deploy
    
    Obtaining EIPs for region: us-east-1, profile: account-one-deploy
    
    Obtaining IPs for network interfaces for region: us-east-1, profile: account-one-deploy
    
    Obtaining EIPs for region: us-east-1, profile: account-three-deploy
    
    Obtaining IPs for network interfaces for region: us-east-1, profile: account-three-deploy
    
    Obtaining EIPs for region: us-east-1, profile: account-six
    
    Obtaining IPs for network interfaces for region: us-east-1, profile: account-six
    
    Obtaining EIPs for region: us-east-1, profile: account-seven
    
    Obtaining IPs for network interfaces for region: us-east-1, profile: account-seven
    
    Obtaining EIPs for region: us-east-1, profile: account-one
    
    Obtaining IPs for network interfaces for region: us-east-1, profile: account-one
    
    Obtained 415 unique elastic IPs from AWS.
    
     
    
     
    
    Takeover possible: {'name': 'takeover.assetnotecloud.com', 'records': ['52.54.24.193']}

## 许可证协议

本项目的开发与发布遵循[ _AGPL_
_-3.0_](https://github.com/assetnote/ghostbuster/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **Ghostbuster：** 【[ _GitHub传送门_](https://github.com/assetnote/ghostbuster)】

## 参考资料

> [
> _https://console.aws.amazon.com/iam/home#/users$new?step=details_](https://console.aws.amazon.com/iam/home#/users$new?step=details)
>
> [ _https://console.aws.amazon.com/iam/home#/users$new?step=permissions
> &accessKey&userNames=ghostbuster&permissionType=policies_](https://console.aws.amazon.com/iam/home#/users$new?step=permissions&accessKey&userNames=ghostbuster&permissionType=policies)
>
> [ _https://dash.cloudflare.com/profile/api-> tokens_](https://dash.cloudflare.com/profile/api-tokens)
>
> [ _https://github.com/infosec-au_](https://github.com/infosec-au)

