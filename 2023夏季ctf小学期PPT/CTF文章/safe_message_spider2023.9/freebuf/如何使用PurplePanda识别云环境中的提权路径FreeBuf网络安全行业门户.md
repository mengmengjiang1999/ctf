![](https://image.3001.net/images/20220323/1648046930_623b3352b7f5a8b344d28.jpg!small)

## 关于PurplePanda

PurplePanda是一款针对云环境安全的强大工具，该工具主要针对紫队安全研究人员设计（当然也适用于红队或蓝队研究人员），可以帮助广大研究人员识别单个云环境或跨云环境的提权路径。

PurplePanda能够从不同的云/SaaS应用程序获取资源，其重点在于关注权限问题上，以便于在云环境/SaaS应用程序配置中识别提权路径或危险权限。值得一提的是，PurplePanda不仅能够搜索目标云环境内的提权问题，而且还支持跨云环境的提权路径识别。

## 支持的平台

> 1、谷歌云平台（GCP）
>
> 2、GitHub
>
> 3、Kubernetes（K8s）

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/carlospolop/PurplePanda

## 工具使用前提

该工具基于Python 3环境开发，因此广大研究人员在使用该工具之前，请先确保已经在本地环境中安装并配置好了Python 3环境。

“/indel”目录（项目根目录中）中定一个每一个文件夹都代表着一个可枚举的平台，

并包含一个自述文件（README.md），该文件会解释如何去使用特定的功能模块。

接下来，我们需要下载Neo4jDesktop并创建一个数据库，然后使用neo4j数据库的URL地址以及密码配置环境变量“PURPLEPANDA_NEO4J_URL”和“PURPLEPANDA_PWD”。

如果你想要在枚举云环境期间结合Shodan搜索引擎来发现公共IP的话，你还需要在名为“SHODAN_KEY”的环境变量中提供有效的Shodan API密钥。

使用下列命令切换到该项目根目录下，然后配置上述参数以及环境变量：

    
    
    cd PurplePanda
    
    python3 -m venv .
    
    source bin/activate
    
    python3 -m pip install -r requirements.txt
    
    export PURPLEPANDA_NEO4J_URL="bolt://neo4j@localhost:7687"
    
    export PURPLEPANDA_PWD="neo4j_pwd_4_purplepanda"
    
    python3 main.py -h # Get help
    
    python3 main.py -e --enumerate google,github,k8s --github-only-org --k8s-get-secret-values --gcp-get-secret-values # Enumerate google, github and k8s

## 工具运行模式

PurplePanda提供了两种分析模式：

> 1、-e（枚举）该模式是该工具的主要模式，它将尝试收集跟目标环境相关的数据并进行分析；
>
> 2、-a（分析）：该模式将使用提供的凭证数据对目标环境执行快速分析；

## 蓝队/紫队使用提示

请在使用该工具时，最好使用能够访问（读取）目标环境全部资源的管理员权限凭证，这样可以准确清楚地获取提权路径信息。

## 红队使用提示

一般来说，云/SaaS平台不会让每个人都能访问平台的配置，这就是为什么PurplePanda支持在同一平台上使用多个密钥，以便尝试列举所有被泄露的密钥，并获得平台配置的最准确视图。

## 工具使用演示

 **视频地址：** https://www.you*tube.com/watch?v=zl5NdvoWHX4

## 项目地址

 **PurplePanda：** 【[ _GitHub传送门_](https://github.com/carlospolop/PurplePanda)】

## 参考资料

> [ _https://github.com/carlospolop/PEASS-> ng_](https://github.com/carlospolop/PEASS-ng)
>
> [ _https://neo4j.com/download-center/#desktop_](https://neo4j.com/download-> center/#desktop)

