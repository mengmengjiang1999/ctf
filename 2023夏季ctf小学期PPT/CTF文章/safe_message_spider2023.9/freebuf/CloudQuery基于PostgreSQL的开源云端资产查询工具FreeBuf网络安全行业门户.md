![](https://image.3001.net/images/20211114/1636896989_619110ddc4483d20b919b.png!small)

## 关于CloudQuery

CloudQuery是一款功能强大的基于PostgreSQL的开源云端资产查询工具，CloudQuery可以帮助广大研究人员将云端资产提取、转移或加载进规范化的PostgreSQL表中。而CloudQuery将帮助我们评估、审核和监控云端资产的安全配置情况。

## CloudQuery关键功能和使用场景

  * 搜索：使用标准SQL语句基于任意配置或关联资产实现任意资产查询。
  * 可视化：将CloudQuery标准PostgreSQL数据库于你指定的BI/虚拟化工具进行连接，比如说Grafana和QuickSight等。
  * Policy-as-Code（策略即代码）：使用SQL作为查询引擎，配置你的安全&策略规则。

## 工具下载&安装

广大研究人员可以点击【[
_这里_](https://github.com/cloudquery/cloudquery/releases)】访问该项目的Releases页面下载CloudQuery的预编译代码。或者，也可以打开命令行终端，使用下列命令来下载安装CloudQuery：

    
    
    export OS=Darwin # 可选值: Linux,Windows,Darwin
    
    curl -L https://github.com/cloudquery/cloudquery/releases/latest/download/cloudquery_${OS}_x86_64 -o cloudquery
    
    chmod a+x cloudquery
    
    ./cloudquery --help
    
    
    # 如果你想要下载指定版本而不使用最新版本，可以使用下列方法
    
    export VERSION= # 指定目标CloudQuery版本号
    
    curl -L https://github.com/cloudquery/cloudquery/releases/download/${VERSION}/cloudquery_${OS}_x86_64 -o cloudquery

### Homebrew安装

    
    
    brew install cloudquery/tap/cloudquery
    
    # 初始安装后，你可以通过下列命令更新CloudQuery版本
    
    brew upgrade cloudquery

## 工具使用

### 工具运行

首先，我们需要生成一个config.hcl文件，该文件负责描述你想要CloudQuery去拉取、转换和规范化的资源。我们可以使用下列命令让CloudQuery获取资源，并将转换的资源规范化处理，然后转换为指定的SQL数据库：

    
    
    cloudquery init aws

获取到了生成的config.hcl文件之后，我们就可以使用下列命令获取云端资源了：

    
    
    docker run -p 5432:5432 -e POSTGRES_PASSWORD=pass -d postgres
    
    cloudquery fetch --dsn "postgres://postgres:pass@localhost:5432/postgres?sslmode=disable"

接下来，运行下列命令查看PostgreSQL数据库信息：

    
    
    psql -h localhost -p 5432 -U postgres -d postgres
    
    
    postgres=# \dt
    
                                        List of relations
    
     Schema |                            Name                             | Type  |  Owner
    
    --------+-------------------------------------------------------------+-------+----------    
     public | aws_autoscaling_launch_configuration_block_device_mapping   | table | postgres
    
     public | aws_autoscaling_launch_configurations                       | table | postgres

此时，我们就可以在psql shell中运行命令来执行下列参考示例了。

### 枚举ec2镜像

    
    
    SELECT * FROM aws_ec2_images;

### 查找所有公开的AWS负载均衡器

    
    
    SELECT * FROM aws_elbv2_load_balancers WHERE scheme = 'internet-facing';

### 运行CloudQuery策略

CloudQuery提供了现成的策略，你可以按原样使用这些策略，也可以根据你的用例进行修改。

比如说，如果你想要运行AWS CIS策略，请输入以下命令（确保通过fetch命令预先获取了所有资源）：

    
    
    ./cloudquery policy run aws-cis-1.2.0

## 编译和运行

    
    
    go build .
    
    ./cloudquery # --help to see all options

## 项目地址

 **CloudQuery：** 【[ _GitHub传送门_](https://github.com/cloudquery/cloudquery)】

## 参考资料

  * [ _https://cloudquery.io/_](https://cloudquery.io/)
  * [ _https://github.com/cloudquery/cloudquery/releases_](https://github.com/cloudquery/cloudquery/releases)
  * [ _https://docs.cloudquery.io/_](https://docs.cloudquery.io/)
  * [ _https://hub.cloudquery.io/_](https://hub.cloudquery.io/)
  * [ _https://github.com/cloudquery/terraform-aws-cloudquery_](https://github.com/cloudquery/terraform-aws-cloudquery)
  * [ _https://hub.cloudquery.io/policies/cloudquery/aws-cis-1.20/latest_](https://hub.cloudquery.io/policies/cloudquery/aws-cis-1.20/latest)
  * [ _https://hub.cloudquery.io/policies_](https://hub.cloudquery.io/policies)

