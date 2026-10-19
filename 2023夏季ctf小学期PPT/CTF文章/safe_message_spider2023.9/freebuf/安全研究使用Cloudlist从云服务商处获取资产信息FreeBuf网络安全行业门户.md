![](https://image.3001.net/images/20210315/1615803050_604f32aa7bc6769f0b05c.png!small)

## Cloudlist

Cloudlist是一款整合了多个云端资源的工具，可以帮助广大研究人员从云服务商那里获取到云端资产的相关信息，比如说主机名称和IP地址等等。该工具主要为蓝队研究人员设计，可以帮助蓝队成员更好地管理和评估云端资产的攻击面，只需很少的配置工作，就可以跨多个云维护一个集中的资产列表。

## 功能介绍

> 可轻松列出具有多种配置的云端资产。
>
> 支持多个云服务商。
>
> 高度可扩展性，支持轻松添加新的云服务商。
>
> STDOUT支持，可在管道中与其他工具配合使用。

## 工具下载

### 源码下载

该工具的下载配置非常简单，我们可以访问该项目的【[
_Releases页面_](https://github.com/projectdiscovery/cloudlist/releases)】下载最新版本的工具预编译代码，使用tar命令提取项目文件后，将其移动到$PATH路径下，然后运行下列命令即可完成工具的配置：

    
    
    tar -xvf cloudlist-linux-amd64.tar
    
    mv cloudlist-linux-amd64 /usr/local/bin/cloudlist
    
    cloudlist -h

### Go下载

Cloudlist的正常运行要求本地主机预先下载并配置好Go v1.14+环境，然后运行下列命令即可获取项目库：

    
    
    GO111MODULE=on go get -v github.com/projectdiscovery/cloudlist/cmd/cloudlist

### GitHub下载

    
    
    git clone https://github.com/projectdiscovery/cloudlist.git; cd cloudlist/cmd/cloudlist; go build; cp cloudlist /usr/local/bin/; cloudlist -version

## 配置文件

默认的工具配置文件存储在“$HOME/.config/cloudlist/config.yaml”路径下，并且包含了配置样例代码。为了保证工具的正常运行，必须更新配置文件中的对应键值：

    
    
    # Configuration file for cloudlist enumeration agent
    
    - # provider is the name of the provider (Digitalocean)
    
      provider: do
    
      # profile is the name of the provider profile
    
      profile: xxxx
    
      # digitalocean_token is the API key for digitalocean cloud platform
    
      digitalocean_token: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    
     
    
    - # provider is the name of the provider (Scaleway)
    
      provider: scw
    
      # scaleway_access_key is the access key for scaleway API
    
      scaleway_access_key: SCWXXXXXXXXXXXXXX
    
      # scaleway_access_token is the access token for scaleway API
    
      scaleway_access_token: xxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxx
    
     
    
    - # provider is the name of the provider (Amazon Web Services)
    
      provider: aws
    
      # profile is the name of the provider profile
    
      profile: staging
    
      # aws_access_key is the access key for AWS account
    
      aws_access_key: AKIAXXXXXXXXXXXXXX
    
      # aws_secret_key is the secret key for AWS account
    
      aws_secret_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    
     
    
    - # provider is the name of the provider (Google Cloud Platform)
    
      provider: gcp
    
      # profile is the name of the provider profile
    
      profile: logs
    
      # gcp_service_account_key is the minified json of a google cloud service account with list permissions
    
      gcp_service_account_key: '{xxxxxxxxxxxxx}'

## 工具使用帮助

    
    
    cloudlist -h

上述命令将显示该工具的帮助菜单，下面给出的是该工具支持的所有参数选项：

 ** **参数****

|

 ** **描述****

|

 ** **使用样例****  
  
---|---|---  
  
config

|

云服务商的配置文件

|

cloudlist -config test.yaml  
  
provider

|

给定云服务商的资产列表

|

cloudlist -provider aws  
  
host

|

主机列表

|

cloudlist -host  
  
ip

|

主机IP

|

cloudlist -ip  
  
json

|

JSON格式输出

|

cloudlist -json  
  
output

|

将输出存储至文件

|

cloudlist -output  
  
silent

|

仅显示结果

|

cloudlist -silent  
  
version

|

显示当前工具版本

|

cloudlist -version  
  
verbose

|

显示Verbose模式

|

cloudlist -verbose  
  
## 工具运行

    
    
    cloudlist

该命令将会把配置文件中配置的云服务商所有对应的资产全部枚举出来，我们还可以使用其他命令来显示指定的云服务商或资产类型：

    
    
    ▶ cloudlist -provider aws
    
     
    
       ________                _____      __
    
      / ____/ /___  __  ______/ / (_)____/ /_
    
     / /   / / __ \/ / / / __  / / / ___/ __/
    
    / /___/ / /_/ / /_/ / /_/ / / (__  ) /_  
    
    \____/_/\____/\__,_/\__,_/_/_/____/\__/  v0.0.1        
    
     
    
        projectdiscovery.io
    
     
    
    [WRN] Use with caution. You are responsible for your actions
    
    [WRN] Developers assume no liability and are not responsible for any misuse or damage.
    
    [INF] Listing assets from AWS (prod) provider.
    
    abc.com
    
    example.com
    
    1.1.1.1
    
    2.2.2.2
    
    3.3.3.3
    
    4.4.4.4
    
    5.5.5.5
    
    6.6.6.6
    
    [INF] Found 2 hosts and 6 IPs from AWS service (prod)

## Nuclei和Cloudlist配合使用

我们还可以跟Nuclei配置使用来从多个云服务商扫描资产以实现安全评估和审计的目的：

    
    
    cloudlist -silent | httpx -silent | nuclei -t cves/

## 支持的云服务商

> AWS（亚马逊Web服务）：EC2、Route53
>
> GCP（谷歌云平台）：Cloud DNS
>
> DO（DigitalOcean）：实例
>
> SCW（Scaleway）：实例

## 以代码库的形式使用Cloudlist

当然了，我们还能够将Coudlist以代码库的方式直接引入到我们的Go程序中。下列代码段演示了如何在Go代码中使用Cloudlist枚举出给定云服务商所有的资产：

    
    
    package main
    
     
    
    import (
    
    "context"
    
    "log"
    
     
    
    "github.com/projectdiscovery/cloudlist/pkg/inventory"
    
    "github.com/projectdiscovery/cloudlist/pkg/schema"
    
    )
    
     
    
    func main() {
    
    inventory, err := inventory.New(schema.Options{
    
    schema.OptionBlock{"provider": "digitalocean", "digitalocean_token": "ec405badb974fd3d891c9223245f9ab5*871c127fce9e632c8dc421edd46d7242"},
    
    })
    
    if err != nil {
    
    log.Fatalf("%s\n", err)
    
    }
    
     
    
    for _, provider := range inventory.Providers {
    
    resources, err := provider.Resources(context.Background())
    
    if err != nil {
    
    log.Fatalf("%s\n", err)
    
    }
    
    for _, resource := range resources.Items {
    
    _ = resource // Do something with the resource
    
    }
    
    }
    
    }

## 工具使用截图

![](https://image.3001.net/images/20210315/1615803131_604f32fb03fbc7656e4ce.png!small)

## 项目地址

Cloudlist：【[ _GitHub传送门_](https://github.com/projectdiscovery/cloudlist)】

## 许可证协议

本项目的开发与发布遵循[
_MIT开源许可证协议_](https://github.com/projectdiscovery/proxify/blob/master/LICENSE.MD)。

## 参考资料

> [
> _https://github.com/BishopFox/smogcloud_](https://github.com/BishopFox/smogcloud)
>
> [ _https://github.com/duo-labs/cloudmapper_](https://github.com/duo-> labs/cloudmapper)
>
> [
> _https://github.com/projectdiscovery/cloudlist/blob/main/PROVIDERS.md_](https://github.com/projectdiscovery/cloudlist/blob/main/PROVIDERS.md)

