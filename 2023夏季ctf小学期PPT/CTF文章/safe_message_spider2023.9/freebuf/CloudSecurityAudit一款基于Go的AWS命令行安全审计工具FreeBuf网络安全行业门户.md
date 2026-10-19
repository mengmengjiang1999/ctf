**cloud-security-audit是一款适用于AWS的命令行安全审计工具。它可以帮助你扫描AWS账户中的漏洞，你将能够快速识别基础架构中不安全的部分，并执行对AWS账户的审计工作。**

## 安装

目前，Cloud Security Audit不支持任何的软件包管理器，目前正在完善这项工作。

## 从源构建

首先，你需要将Cloud Security Audit下载到GO工作区：

    
    
    $GOPATH $ go get github.com/Appliscale/cloud-security-audit
    $GOPATH $ cd cloud-security-audit

然后，通过执行以下命令在cloud-security-audit目录中构建和安装应用程序配置：

    
    
    cloud-security-audit $ make all

## 使用

###  **初始化会话**

如果你正在使用MFA，则需要在进行连接之前尝试使用flag -mfa告知Cloud Security Audit对你进行身份验证。例如：

    
    
    $ cloud-security-audit --service s3 --mfa --mfa-duration 3600

###  **EC2扫描**

要对所有EC2实例执行审计，请键入以下命令：

    
    
    $ cloud-security-audit --service ec2

你可以使用-r或--region，将审计范围缩小至某个区域。Cloud Security Audit还支持AWS配置文件 - 指定配置文件使用-p或--profile标志。

 **输出示例：**

    
    
    +---------------+---------------------+--------------------------------+-----------------------------------+----------+
    | AVAILABILITY  |         EC2         |            VOLUMES             |             SECURITY              |          |
    |               |                     |                                |                                   | EC2 TAGS |
    |     ZONE      |                     |     (NONE) - NOT ENCRYPTED     |              GROUPS               |          |
    |               |                     |                                |                                   |          |
    |               |                     |    (DKMS) - ENCRYPTED WITH     |    (INCOMING CIDR = 0.0.0.0/0)    |          |
    |               |                     |         DEFAULT KMSKEY         |                                   |          |
    |               |                     |                                |       ID : PROTOCOL : PORT        |          |
    +---------------+---------------------+--------------------------------+-----------------------------------+----------+
    | eu-central-1a | i-0fa345j6756nb3v23 | vol-0a81288qjd188424d[DKMS]    | sg-aaaaaaaa : tcp : 22            | App:some |
    |               |                     | vol-0c2834re8dfsd8sdf[NONE]    | sg-aaaaaaaa : tcp : 22            | Key:Val  |
    +---------------+---------------------+--------------------------------+-----------------------------------+----------+

 **对以上输出的解读：**

> 第一列 AVAILABILITY ZONE包含放置实例的信息；
>
> 第二列 EC2包含实例ID；
>
> 第三列 卷包含给定EC2的附加卷（虚拟磁盘）的ID。

 **后缀含义：**

> [NONE] - 卷未加密；
>
> [DKMS] -> 使用AWS默认KMS密钥加密的卷。有关KMS的更多信息，请[点击此处](https://aws.amazon.com/kms/faqs/)；
>
> 第四列 安全组包含权限过于开放的安全组的ID。例如CIDR块为0.0.0.0/0（对全球开放）；
>
> 第五列 EC2 TAGS包含给定EC2实例的标记，以帮助你识别此实例的用途。

 **文档**

你可以在以下文档中找到有关加密的更多信息：

> <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSEncryption.html>

### S3扫描

要对所有S3 buckets执行审计，请键入以下命令：

    
    
    $ cloud-security-audit --service s3

Cloud Security Audit支持AWS配置文件 - 指定配置文件使用-p或--profile标志。

 **输出示例：**

    
    
    +------------------------------+---------+---------+-------------+------------+
    |          BUCKET NAME         | DEFAULT | LOGGING |     ACL     |  POLICY    |
    |                              |         |         |             |            |
    |                              |   SSE   | ENABLED |  IS PUBLIC  | IS PUBLIC  |
    |                              |         |         |             |            |
    |                              |         |         |  R - READ   |  R - READ  |
    |                              |         |         |             |            |
    |                              |         |         |  W - WRITE  | W - WRITE  |
    |                              |         |         |             |            |
    |                              |         |         | D - DELETE  | D - DELETE |
    +------------------------------+---------+---------+-------------+------------+
    | bucket1                      | NONE    | true    | false       | false      |
    +------------------------------+---------+---------+-------------+------------+
    | bucket2                      | DKMS    | false   | false       | true [R]   |
    +------------------------------+---------+---------+-------------+------------+
    | bucket3                      | AES256  | false   | true [RWD]  | false      |
    +--------------------------- --+---------+---------+-------------+------------+

 **对以上输出的解读：**

第一列 BUCKET NAME包含s3 buckets的名称；

第二列 DEFAULT SSE为你提供有关在s3 buckets中使用哪种默认服务器端加密类型的信息：

> NONE - 未启用默认SSE；
>
> DKMS - 启用默认SSE，用于加密数据的AWS KMS密钥；
>
> AES256 - 启用默认SSE，AES256。

如果为给定的s3 buckets启用了服务器访问日志记录，则第三列LOGGING ENABLED包含信息。这提供了对s3
buckets发出的请求的详细记录。有关服务器访问日志记录的更多信息，请[点击这里](https://docs.aws.amazon.com/AmazonS3/latest/user-guide/server-access-logging.html)。

第四列 ACL IS
PUBLIC在ACL（访问控制列表）包含使bucket成为公共（允许任何人读/写）的权限时提供信息。有关ACL的更多信息，请[点击这里](https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html)。

如果bucket的策略允许匿名用户执行任意操作（读/写），则第五列POLICY IS
PUBLIC包含信息。有关bucket策略的更多信息，请在[此处查看](https://docs.aws.amazon.com/AmazonS3/latest/dev/using-iam-policies.html)。R，W和D字母描述了适用于每个人的操作类型。

##  **文档**

你可以在以下文档中找到有关S3安全的更多信息：

> [https://docs.aws.amazon.com/AmazonS3/latest/dev/serv-side-encryption.html
> ](https://docs.aws.amazon.com/AmazonS3/latest/dev/serv-side-encryption.html)
>
> <https://docs.aws.amazon.com/AmazonS3/latest/dev/ServerLogs.html>
>
> <https://docs.aws.amazon.com/AmazonS3/latest/user-guide/server-access-> logging.html>

***参考来源：[GitHub](https://github.com/Appliscale/cloud-security-audit)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

