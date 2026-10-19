![](https://image.3001.net/images/20220323/1648045189_623b2c85bbd3d9cfdb100.jpeg!small)

## 关于s3sec

s3sec 是一款专门针对 AWS S3 实例的安全检测工具，在该工具的帮助下，广大研究人员可以轻松检测目标AWS S3
Buckets的读取、写入和删除权限。

该工具的主要目标是为了快速测试S3 Buckets列表中实例的安全性，从而在漏洞奖励计划中给广大渗透测试人员提供辅助。

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/0xmoot/s3sec

## 工具使用

 **检查单个S3实例：**

    
    
    echo "test-instance.s3.amazonaws.com" | python3 s3sec.py

 **或者：**

    
    
    echo "test-instance" | python3 s3sec.py

 **检查S3实例列表（多个实例）：**

    
    
    cat locations | python3 s3sec.py

## 配置AWS CLI & 凭证

如需使用该工具的完整功能，我们还要安装AWS CLI，并配置用户证书。

安装好AWS CLI之后，我们将能够使用s3sec所提供的一系列更加高级的测试功能，其中包括未签名的读取、写入文件和删除文件。

### 在Kali Linux上安装AWS CLI

我们可以直接使用下列命令来安装AWS CLI：

    
    
    pip3 install awscli

### 获取AWS凭证（访问密钥ID和AWS秘密访问密钥）

> 1、在亚马逊的AWS官方网站上注册：【[ _传送门_](https://aws.amazon.com/free/?all-free-tier.sort-> by=item.additionalFields.SortRank&all-free-tier.sort-order=asc)】；
>
> 2、登录你的AWS账号，并点击“My Security Credentials”（我的安全凭证）；
>
> 3、点击“Access Keys”（访问密钥），获取AWS CLI所需的登录凭证，即访问密钥ID和秘密访问密钥；
>
> 4、接下来，点击“Show Access Key”选项来获取你的访问密钥ID和秘密访问密钥，或者也可以直接将它们下载下来。

### 在Kali Linux上配置AWS CLI

首先，打开一个终端窗口，然后输入下列命令：

    
    
    aws configure

接下来，输入你在刚才所获取到的AWS访问密钥ID和AWS秘密访问密钥，数据格式如下所示：

    
    
    AWS Access Key Id: <<Your Key>>
    
    AWS Secret Access Key: <<Your Secret Access Key>>
    
    Default region name: ap-south-1
    
    Default output format: json

## 工具运行截图

![](https://image.3001.net/images/20220323/1648045280_623b2ce076901446856d7.png!small)

## 许可证协议

本项目的开发与发布遵循MIT开源许可证协议。

## 项目地址

 **s3sec：** 【[ _GitHub传送门_](https://github.com/0xmoot/s3sec)】

## 参考资料

> [ _https://aws.amazon.com/free/?all-free-tier.sort-> by=item.additionalFields.SortRank &all-free-tier.sort-> order=asc_](https://aws.amazon.com/free/?all-free-tier.sort-> by=item.additionalFields.SortRank&all-free-tier.sort-order=asc)

