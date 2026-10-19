## 前言

 **今天给大家介绍的是一款名叫CloudMapper的开源工具，该工具由Duo Security公司开发，主要针对的是Amazon Web
Service（AWS）云环境。**

![工具一览图](https://image.3001.net/images/20180816/1534396103_5b7506c7e2edb.png!small)

## 工具介绍

CloudMapper可以帮助研究人员分析Amazon
WebService(AWS)环境的安全性，该工具原本的目的是为了生成网络结构图并在浏览器中呈现出来，现在已经增加了很多新的功能。

在组织获取企业中，会有很多团队同时在运行多个项目，因此就会涉及到大量的AWS账号，而CloudMapper可以帮助组织更好地管理自己的AWS资产。

> 在CloudMapper的帮助下，我们可以迅速了解到下列情况：
>
> 哪一个资源是公开可访问的？
>
> 哪一个资源可以跟内部其他资源通信？
>
> 整个网络体系结构是否安全？
>
> 账号的资源使用情况以及结构复杂度？

![架构图](https://image.3001.net/images/20180816/1534396119_5b7506d737edd.png!small)

## 工具安装

依赖组件：

除了Python
3、pip和virtualenv之外，你还需要用到[jq](https://stedolan.github.io/jq/)和[pyjq](https://github.com/doloopwhile/pyjq)库。

### macOS平台

    
    
    #clone the repo
    
    git clone git@github.com:duo-labs/cloudmapper.git
    
    #Install pre-reqs for pyjq
    
    brew install autoconf automake libtool jq awscli python3
    
    cd cloudmapper/
    
    python3-m venv ./venv
    
    source venv/bin/activate
    
    pip install -r requirements.txt

### Linux平台

    
    
    #clone the repo
    
    git clone git@github.com:duo-labs/cloudmapper.git
    
    #(Centos, Fedora, RedHat etc.):
    
    #sudo yum install autoconf automake libtool python34-devel jq awscli
    
    #(Debian, Ubuntu etc.):
    
    # Youmay additionally need "build-essential"
    
    sudo apt-get install autoconf automake libtool python3-dev jq awscli
    
    cd cloudmapper/
    
    python3 -m venv ./venv
    
    source venv/bin/activate
    
    pip install -r requirements.txt

## 导入演示数据

项目自带了一套演示数据集，你可以使用下列命令导入演示数据（可参考<https://duo-labs.github.io/cloudmapper/>）：

    
    
    python cloudmapper.py prepare --config config.json.demo --account demo
    
    python cloudmapper.py webserver

本地Web服务器地址为<http://127.0.0.1:8000/>。

## 工具配置

### 第一步：创建你的账号

选项1：手动编辑配置文件

将文件config.json.demo更名为config.json，填入你的账号ID、名称和外部CIDR名。CIDR为一个IP地址范围，例如1.2.3.4/32。

选项2：生成配置文件

CloudMapper提供了账号相关的配置命令：

    
    
    python cloudmapper.py configure {add-account|remove-account} --config-file CONFIG_FILE--name NAME --id ID [--default DEFAULT]
    
    python cloudmapper.py configure {add-cidr|remove-cidr} --config-file CONFIG_FILE --cidrCIDR --name NAME

这些命令可以帮助你定义相同环境下的不同AWS账号，并获取到对应的CIDR IP。

### 第二步：收集账号数据

这一步需要使用CLI来调用describe和list，并将相关账号数据以JSON格式存储到account-data之中。

## AWS权限要求

你必须拥有AWS凭证的可读权限才可以保证CLI的正常运行（数据读取与收集），我建议大家使用[aws-vault](https://github.com/99designs/aws-vault)。CloudMapper还可以收集IAM信息，因此你还需要使用到MFA，只有账号数据收集那一步需要用到AWS访问权。

你需要提供的权限如下：

    
    
    arn:aws:iam::aws:policy/SecurityAudit
    
    arn:aws:iam::aws:policy/job-function/ViewOnlyAccess

额外的参考数据如下：

    
    
    {
    
        "Version":"2012-10-17",
    
        "Statement": [
    
            {
    
                "Action": [
    
                    "acm:DescribeCertificate",
    
                    "apigateway:GET",
    
                   "ec2:DescribeLaunchTemplates",
    
                   "eks:DescribeCluster",
    
                    "eks:ListClusters",
    
                   "elasticfilesystem:DescribeMountTargetSecurityGroups",
    
                   "elasticfilesystem:DescribeMountTargets",
    
                   "elasticmapreduce:DescribeCluster",
    
                   "elasticmapreduce:DescribeSecurityConfiguration",
    
                   "events:DescribeRule",
    
                    "fms:ListComplianceStatus",
    
                    "fms:ListPolicies",
    
                   "guardduty:ListDetectors",
    
                   "guardduty:ListFindings",
    
                   "guardduty:ListIPSets",
    
                   "guardduty:ListInvitations",
    
                    "guardduty:ListMembers",
    
                   "guardduty:ListThreatIntelSets",
    
                   "iam:GetSSHPublicKey",
    
                   "inspector:DescribeAssessmentRuns",
    
                   "inspector:DescribeAssessmentTargets",
    
                    "inspector:DescribeAssessmentTemplates",
    
                   "inspector:DescribeCrossAccountAccessRole",
    
                   "inspector:DescribeFindings",
    
                   "inspector:DescribeResourceGroups",
    
                   "inspector:DescribeRulesPackages",
    
                    "iot:DescribeAuthorizer",
    
                   "iot:DescribeCACertificate",
    
                   "iot:DescribeCertificate",
    
                   "iot:DescribeDefaultAuthorizer",
    
                    "iot:GetPolicy",
    
                   "iot:GetPolicyVersion",
    
                    "lambda:GetFunctionConfiguration",
    
                   "lightsail:GetInstances",
    
                   "lightsail:GetLoadBalancers",
    
                   "opsworks:DescribeStacks",
    
                   "organizations:DescribeAccount",
    
                   "organizations:DescribeCreateAccountStatus",
    
                   "organizations:DescribeHandshake",
    
                   "organizations:DescribeOrganization",
    
                   "organizations:DescribeOrganizationalUnit",
    
                   "organizations:DescribePolicy",
    
                    "organizations:ListAWSServiceAccessForOrganization",
    
                   "shield:DescribeAttack",
    
                   "shield:DescribeProtection",
    
                   "shield:DescribeSubscription",
    
                   "sso:DescribePermissionsPolicies",
    
                    "sso:ListApplicationInstanceCertificates",
    
                   "sso:ListApplicationInstances",
    
                   "sso:ListApplicationTemplates",
    
                   "sso:ListApplications",
    
                   "sso:ListDirectoryAssociations",
    
                    "sso:ListPermissionSets",
    
                   "sso:ListProfileAssociations",
    
                    "sso:ListProfiles"
    
                ],
    
                "Resource":"*",
    
                "Effect":"Allow"
    
            }
    
        ]
    
    }

## 收集数据

收集数据的操作命令如下：

    
    
    python cloudmapper.py collect --account my_account

### 命令简介

-api_endpoints：可通过API Gateway调用的URL列表；

-audit：检查可能存在的错误配置；

-collect：收集关于源账号的详细数据；

-find_admins：通过分析IAM策略识别管理员用户和角色，并发现潜在的IAM问题；

-prepare/webserver：可视化查看网络架构；

-public：寻找公共主机和IP地址范围；

-sg_ips：获取地理位置信息；

-stats：查看账号资源数量；

## 使用到的其他项目

  * cytoscape.js: MIT [https://github.com/cytoscape/cytoscape.js/blob/master/LICENSE](https://github.com/cytoscape/cytoscape.js/blob/master/LICENSE)
  * cytoscape.js-qtip: MIT [https://github.com/cytoscape/cytoscape.js-qtip/blob/master/LICENSE](https://github.com/cytoscape/cytoscape.js-qtip/blob/master/LICENSE)
  * cytoscape.js-grid-guide: MIT [https://github.com/iVis-at-Bilkent/cytoscape.js-grid-guide](https://github.com/iVis-at-Bilkent/cytoscape.js-grid-guide)
  * cytoscape.js-panzoom: MIT [https://github.com/cytoscape/cytoscape.js-panzoom/blob/master/LICENSE](https://github.com/cytoscape/cytoscape.js-panzoom/blob/master/LICENSE)
  * jquery: JS Foundation [https://github.com/jquery/jquery/blob/master/LICENSE.txt](https://github.com/jquery/jquery/blob/master/LICENSE.txt)
  * jquery.qtip: MIT [https://github.com/qTip2/qTip2/blob/master/LICENSE](https://github.com/qTip2/qTip2/blob/master/LICENSE)
  * cytoscape-navigator: MIT [https://github.com/cytoscape/cytoscape.js-navigator/blob/c249bd1551c8948613573b470b30a471def401c5/bower.json#L24](https://github.com/cytoscape/cytoscape.js-navigator/blob/c249bd1551c8948613573b470b30a471def401c5/bower.json#L24)
  * cytoscape.js-autopan-on-drag: MIT [https://github.com/iVis-at-Bilkent/cytoscape.js-autopan-on-drag](https://github.com/iVis-at-Bilkent/cytoscape.js-autopan-on-drag)
  * font-awesome: MIT [http://fontawesome.io/](http://fontawesome.io/)
  * FileSave.js: MIT [https://github.com/eligrey/FileSaver.js/blob/master/LICENSE.md](https://github.com/eligrey/FileSaver.js/blob/master/LICENSE.md)
  * circular-json: MIT [https://github.com/WebReflection/circular-json/blob/master/LICENSE.txt](https://github.com/WebReflection/circular-json/blob/master/LICENSE.txt)
  * rstacruz/nprogress: MIT [https://github.com/rstacruz/nprogress/blob/master/License.md](https://github.com/rstacruz/nprogress/blob/master/License.md)
  * mousetrap: Apache [https://github.com/ccampbell/mousetrap/blob/master/LICENSE](https://github.com/ccampbell/mousetrap/blob/master/LICENSE)
  * akkordion MIT <https://github.com/TrySound/akkordion/blob/master/LICENSE>

*** 参考来源：[cloudmapper](https://github.com/duo-labs/cloudmapper)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

