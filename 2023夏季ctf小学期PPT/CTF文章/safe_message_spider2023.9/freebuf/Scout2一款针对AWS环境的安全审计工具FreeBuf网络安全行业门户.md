**今天给大家介绍的是一款名叫Scout2的安全审计工具，广大安全研究人员可以用它来对AWS环境的安全性进行检测。**

![Scout2：一款针对AWS环境的安全审计工具](https://image.3001.net/images/20180728/1532736807_5b5bb52722c08.png!small)

## AWS Scout2

Scout2是一款针对AWS环境的安全审计工具，在Scout2的帮助下，AWS管理员能够迅速了解各自AWS环境的安全状态。Scout2能够利用AWS
API来收集AWS环境的配置数据，以便研究人员进行手动安全审计，并且Scout2还会自动将高风险区域高亮标记。需要注意的是，Scout2最大的优势就是能够自动化地给研究人员呈现出清晰的攻击面信息，而不像其他的工具那样需要进行繁琐的操作。

注意：目前Scout2的开发人员仍在对该项目进行积极地升级与维护，因此工具的某些功能和内部接口可能会发生变化。如果你在使用Scout2的过程中遇到了bug，请及时在本项目的[GitHub主页](https://github.com/nccgroup/Scout2)提供反馈信息。

## 工具安装

通过[pip](https://pip.pypa.io/en/stable/index.html)安装：

    
    
    $ pip install awsscout2

通过git克隆源码：

    
    
    $ git clone https://github.com/nccgroup/Scout2
    $ cd Scout2
    $ pip install -r requirements.txt
    $ python setup.py install

## 工具要求

### 计算资源

Scout2是一款多线程工具，在工具的运行过程中，它能够获取你的AWS账号配置信息并存储在内存中。该工具可以在大多数现代笔记本电脑和等价虚拟机中正常运行，不过由于虚拟机的可用计算资源有限，其进程很可能会被终止运行。

### Python

Scout2采用Python开发，并且支持下列版本：

> Python2.7
>
> Python3.3
>
> Python3.4
>
> Python3.5
>
> Python3.6

### AWS凭证

运行Scout2之前，你需要一个有效的AWS凭证（例如Access Key ID和Secret Access
Key）。跟指定凭证绑定的用户角色或用户账号至少需要拥有对所有服务资源的只读权限，这些服务包括但不仅限于CloudTrail、EC2、IAM、RDS、Redshift和S3。

为了获取到必要的权限，下列AWS管理策略需要添加至规则中：

    
    
    ReadOnlyAccess
    SecurityAudit

### AWS的可接受使用策略（AUP）

在使用Scout2的过程中，AWS用户并不需要填写并提交AWS漏洞/渗透测试请求表，Scout2只会执行AWS
API调用来获取AWS环境的配置数据并识别安全风险，因此这种行为并不会被当作是安全扫描行为，并且不会影响AWS的网络和应用程序。

## 工具使用

执行了一系列AWS API调用之后，Scout2会创建一个本地HTML报告，并使用设备默认浏览器将报告呈现给用户。如果你的设备已经配置好了AWS
CLI、boto3或其他AWS SDK的话，你就可以通过下列命令启动Scout2了：

    
    
    $ Scout2

如果你的.aws/credentials和.aws/config文件中包含了多条配置信息的话，你还可以使用下列命令指定需要使用的凭证：

    
    
    $ Scout2 --profile <PROFILE_NAME>

如果你拥有一个包含了API访问密钥和secret的CSV文件，你还可以使用下列命令来运行Scout2：

    
    
    $ Scout2 --csv-credentials <CREDENTIALS.CSV>

## 详细文档

下面的命令可以给你提供所有可用的命令行选项列表：

    
    
    $ Scout2 –help

如果你想了解更多详细信息，请参考这篇【[Wiki文档](https://github.com/nccgroup/Scout2/wiki)】。

### 许可证信息

本项目遵循GPLv2许可证协议。

 ***
参考来源：[Scout2](https://github.com/nccgroup/Scout2)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

