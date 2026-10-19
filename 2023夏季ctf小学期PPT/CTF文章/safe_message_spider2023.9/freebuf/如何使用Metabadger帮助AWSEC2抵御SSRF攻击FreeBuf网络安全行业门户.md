![](https://image.3001.net/images/20211123/1637662400_619cbec00f900c64585fe.jpg!small)

## 关于Metabadger

Metabadger是一款功能强大的SSRF攻击防护工具，该工具可以帮助广大研究人员通过自动升级到更安全的实例元数据服务v2（IMDSv2），以防止网络犯罪分子对AWS
EC2发动SSRF攻击。

## 功能介绍

  * 诊断和评估AWS实例元数据服务的当前使用情况，并了解该服务的工作方式；
  * 升级到实例元数据服务v2（IMDSv2），以防范针对v1的攻击向量；
  * 专门更新实例以仅使用IMDSv2；
  * 在不需要的情况下禁用实例元数据服务，以减少攻击面；

## AWS实例元数据服务是什么？

本质上来说，AWS元数据服务将允许用户访问实例中的所有内容，包括实例角色凭据和会话令牌等。实例元数据是有关用户的实例的数据，可以用来配置或管理正在运行的实例。实例元数据可划分成不同类别。

重要注意的是，虽然用户只能从实例自身内部访问实例元数据和用户数据，但数据并未进行加密保护。可访问实例的人员均可查看其元数据。因此，用户应当采取适当的预防措施来保护敏感数据（例如永久加密密钥），而不应将敏感数据
(例如密码) 存储为用户数据。

用户也可以使用实例元数据访问用户启动实例时指定的用户数据。例如，用户可指定参数以便配置实例，也可附加简单的脚本。用户也可以使用这些数据来构建更多可通过启动时提供的配置文件来修改的通用AMI。例如，如果用户为各种小型企业运行
Web 服务器，则这些企业都可以使用相同的 AMI，并在启动时从用户在用户数据中指定的 Amazon S3
存储桶中检索其各自的内容。要随时添加一个新客户，用户只需为该客户创建一个存储桶，将客户的内容添加进去，然后启动用户的 AMI
即可。如果用户同时启动多个实例，则用户数据可供该预留中的所有实例使用。

## 工具要求

Metabadger需要带有下列权限的IAM角色或凭证：

    
    
    ec2:ModifyInstanceAttribute
    
    ec2:DescribeInstances

在对实例元数据服务进行更改时，我们应该谨慎，并遵循AWS关于如何安全升级到v2的[
_其他指导_](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html)。Metabadger旨在帮助我们以自动化的方式完成此过程，以进一步保护AWS中的计算基础设施。

## 工具安装

### 通过pip安装

    
    
    pip3 install --user metabadger

### 通过GitHub安装

    
    
    $ git clone https://github.com/salesforce/metabadger
    
    $ cd metabadger
    
    $ pip install -e .
    
     
    
    $ metabadger
    
    Usage: metabadger [OPTIONS] COMMAND [ARGS]...
    
     
    
      Metabadger is an AWS Security Tool used for discovering and hardening the
    
      Instance Metadata service.
    
     
    
    Options:
    
      --version  Show the version and exit.
    
      --help     Show this message and exit.
    
     
    
    Commands:
    
      disable-metadata     Disable the IMDS service on EC2 instances
    
      discover-metadata    Discover summary of IMDS service usage within EC2
    
      discover-role-usage  Discover summary of IAM role usage for EC2
    
      harden-metadata      Harden the AWS instance metadata service from v1 to v2

## 工具使用

### discover-metadata

查看实例元数据服务总体使用情况的摘要，包括版本和总体实施百分比。使用这些数字将有助于我们了解元数据使用的总体状况：

    
    
    Options:
    
      -a, --all-region    Provide a metadata summary for all available regions in the AWS account
    
      -j, --json          Get metadata summary in JSON format
    
      -r, --region TEXT   Specify which AWS region you will perform this command in
    
      -p, --profile TEXT  Specify the AWS IAM profile.

### discover-role-usage

通过对实例及其使用的角色的总结，我们可以很好地了解在更新元数据服务本身时必须注意的事项：

    
    
    Options:
    
      -p, --profile TEXT  Specify the AWS IAM profile.
    
      -r, --region TEXT   Specify which AWS region you will perform this command in

### harden-metadata

能够修改实例以使用元数据v1或v2：

    
    
    Options:
    
      -a, --all-region       Update IMDS across all regions in your account
    
      -e, --exclusion        The exclusion flag will apply to everything besides what is specified, tags or instances
    
      -d, --dry-run          Dry run of hardening metadata changes
    
      -v1, --v1              Enforces v1 of the metadata service
    
      -i, --input-file PATH  Path of csv file of instances to harden IMDS for
    
      -t, --tags TEXT        A comma seperated list of tags to apply the hardening setting to
    
      -r, --region TEXT      Specify which AWS region you will perform this command in
    
      -p, --profile TEXT     Specify the AWS IAM profile.

### disable-metadata

该命令将会在实例中完全禁用元数据服务：

    
    
    Options:
    
      -e, --exclusion        The exclusion flag will apply to everything besides what is specified, tags or instances
    
      -d, --dry-run          Dry run of disabling the metadata service
    
      -i, --input-file PATH  Path of csv file of instances to disable IMDS for
    
      -t, --tags TEXT        A comma seperated list of tags to apply the hardening setting to
    
      -r, --region TEXT      Specify which AWS region you will perform this command in
    
      -p, --profile TEXT     Specify the AWS IAM profile.

## 工具使用演示样例

![](https://image.3001.net/images/20211123/1637662474_619cbf0ac25d98b214300.gif)

## 项目地址

 **Metabadger：** 【[ _GitHub传送门_](https://github.com/salesforce/metabadger)】

## 参考资料

  * [ _https://awscli.amazonaws.com/v2/documentation/api/latest/reference/ec2/modify-instance-metadata-options.html_](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/ec2/modify-instance-metadata-options.html)
  * [ _https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html_](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html)

