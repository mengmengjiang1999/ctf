**今天给大家介绍的是一款名叫Pacu的开源AWS[漏洞利用](https://www.kitploit.com/search/label/Exploitation)框架，该工具可以帮助广大开发人员检测AWS云环境的安全状况。**

![a.png](https://image.3001.net/images/20181121/1542813754_5bf5783a82064.png!small)

在Pacu的帮助下，测试人员可以利用AWS账号中的错误配置漏洞，而且可以通过使用模块的方式来扩展工具的功能。当前的模块支持大量常见的攻击场景，包括用户提权、IAM用户植入后门以及攻击存在安全缺陷的Lambda函数等等。

## 工具安装

Pacu是一款轻量级工具，它要求使用Python
3.5+，并需要通过pip3来安装其他Python库。运行install.sh之后，脚本会检查你的Python版本，并确保所有的Python包都是最新版本。

### 快速安装

    
    
    git clone <https://github.com/RhinoSecurityLabs/pacu>
    
    cd pacu
    
    bash install.sh
    
    python3 pacu.py

具体的安装指令，请参考【[安装指引](https://github.com/RhinoSecurityLabs/pacu/wiki/Installation)】。

## 工具使用

Pacu首次启动之后，工具将提示用户开启和命名新的会话。这个会话将用来存储AWS密钥对，以及其他通过运行模块收集到的数据。你可以在Pacu中开启各种不同的会话，每一个会话都拥有各自对应的AWS密钥对以及数据集。

模块的使用同样需要AWS密钥，这个密钥会给你提供AWS环境的访问权。如果你在使用中遇到了困难。可以使用help命令来查看可用命令的列表。

### Pacu的基础命令

> >list：该命令可以列举出所有可用的模块；
>
> >helpmodule_name：该命令将返回特定模块的帮助信息；
>
> >runmodule_name：该命令可以配合特定的参数来运行指定的模块；
>
> > runmodule_name --regions eu-west-1、us-west-1：该命令将针对eu-west-1和us-> west-1这两个区域运行指定模块；

## 提交请求&漏洞报告

1、
大家可以直接通过电子邮件：pacu@rhinosecuritylabs.com上报Pacu的[漏洞信息](https://www.kitploit.com/search/label/vulnerabilities)；

2、 Pacu在每一个会话目录中都创建了错误日志，并且还通过全局错误日志来记录主目录下创建的会话错误。如果可以的话，大家尽量把这些日志一起发送给我们。

3、
如果你想添加额外的功能，或者有其他的想法，，可以从【[这里](https://github.com/RhinoSecurityLabs/pacu/issues/new/choose)】告诉我们。

## Pacu的模块功能

Pacu使用了大量插件模块来协助测试人员在AWS环境下实现数据枚举、权限提升、数据提取、服务漏洞利用和日志篡改等活动。目前，Pacu提供了36种不同的针对AWS的攻击模块，而且我们仍在开发新的功能模块（新模块即将上线）。

为了适应现有的AWS产品环境，我们在开发模块时使用的是常用的语句和数据结构，并且使用了本地SQLite数据库来存储和管理收集到的数据，与此同时，我们尽量减少了API的调用。除此之外，我们还在框架中整合了漏洞报告和攻击审计的功能，可以帮助研究人员完善测试报告。

### 开发Pacu模块

如果你想开发自己的Pacu模块的话，可以先看看这篇【[指引文档](https://github.com/RhinoSecurityLabs/pacu/wiki/Module-Development-Guide)】，我们强烈欢迎社区的广大研究人员贡献自己的代码！

### 注意事项

> 1、 Pacu目前仅支持macOS和Linux环境。
>
> 2、 Pacu是一款开源软件，遵循BSD-3-Clause许可证协议。

***参考来源：[RhinoSecurityLabs](https://github.com/RhinoSecurityLabs/pacu)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

