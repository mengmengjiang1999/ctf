![lightbulb-framework_1.png](https://image.3001.net/images/20190131/1548905901_5c526dad8e2c5.png!small)

**[LightBulb](https://github.com/lightbulb-framework/lightbulb-framework)是一个基于python的，用于审计web应用程序防火墙和过滤器的开源框架。**

该框架包含了以下两个主要算法：

> **GOFA**
> ：一种主动学习算法，在在标准的等价查询模型中自动推断符号并表示。主动学习算法允许远程分析过滤器和Sanitizer程序，即只允许查询目标程序并观察输出。
>
> **SFADiff**
> ：一种基于符号有限自动机（SFA）学习的黑盒测试算法。查找具有类似功能程序之间的差异是一个重要的安全问题，因为这些差异可用于指纹识别或针对安全软件（如Web应用防火墙（WAF））的规避攻击，这些安全软件旨在检测Web应用程序的恶意输入。

## 动机

Web应用防火墙（WAF）是现代应用程序安全性的重要保障之一。例如，处理信用卡交易组织的PCI标准就规定，面向互联网的任何应用程序都应受到WAF保护或已通过标准的代码审计流程，但审计Web应用防火墙仍是一项具有挑战性且复杂的任务。查找绕过防火墙的攻击方法，通常都需要具备专业领域的知识。因此，没有掌握这种技能的渗透测试人员会留下公开的攻击字符串列表，如XSS
Cheat Sheet，这些列表通常不足以全面评估WAF产品的安全性。

##  **命令使用**

主界面命令：

命令 | 描述  
---|---  
core | 显示可用的core模块  
utils | 显示可用的查询处理程序  
info <module> | 打印模块信息  
library | 进入library  
modules | 显示可用的应用模块  
use <module> | 进入模块  
start <moduleA> <moduleB> | 启动算法  
help | 打印帮助信息  
status | 检查并安装需要的软件包  
complete | 打印bash完成命令  
  
模块命令：

命令 | 描述  
---|---  
back | 返回到主菜单  
info | 打印当前模块信息  
library | 进入library  
options | 显示可用选项  
define <option> <value> | 设置选项值  
start | 启动算法  
complete | 打印bash完成命令  
  
Library 命令：

命令 | 描述  
---|---  
back | 返回到主菜单  
info <folder\module> | 打印请求的模块信息（文件夹必须位于lightbulb/data/）  
cat <folder\module> | 打印请求的模块（文件夹必须位于lightbulb/data/）  
modules <folder> | 在请求的文件夹中显示可用的库模块（文件夹必须位于lightbulb/data/）  
search <keywords> | 使用逗号分隔的关键字搜索可用的库模块  
complete | 打印bash完成命令  
  
## 安装

### 系统准备

首先，你必须先验证你的系统是否支持flex，python dev，pip和build：

对于apt平台（如ubuntu，debian等）：

    
    
    sudo apt-get install flex
    sudo apt-get install python-pip
    sudo apt-get install python-dev
    sudo apt-get install build-essential

（apt可选）如要添加对MySQL测试的支持：

    
    
    sudo apt-get install libmysqlclient-dev

对于已安装了额外软件包repo（epel-release）的yum平台（如centos，redhat，fedora等）：

    
    
    sudo yum install -y python-pip
    sudo yum install -y python-devel
    sudo yum install -y wget
    sudo yum groupinstall -y 'Development Tools'

（yum可选）如要添加对MySQL测试的支持：

    
    
    sudo yum install -y mysql-devel 
    sudo yum install -y MySQL-python

###  **安装** **Lightbulb**

在没有完整包安装的情况下使用应用程序：

    
    
    git clone https://github.com/lightbulb-framework/lightbulb-framework
    cd lightbulb-framework
    make
    lightbulb status

为了执行完整的包安装，你也可以从pip存储库来安装它。前提是你已安装最新的setuptools版本：

    
    
    pip install setuptools --upgrade
    pip install lightbulb-framework
    lightbulb status

如果你想使用virtualenv：

    
    
    pip install virtualenv
    virtualenv env
    source env/bin/activate
    pip install lightbulb-framework
    lightbulb status

“lightbulb
status”命令将引导你安装对MySQLdb和OpenFst的支持。如果在linux中使用virtualenv，则只需安装libmysqlclient-dev软件包（需要sudo）。

应该注意的是，如果要使用Burp Extension，则不需要执行“lightbulb
status”命令。原因是该命令安装了“openfst”和“mysql”bindings，默认情况下扩展名使用的是Jython，不支持C
bindings。建议仅在希望从设置更改burp扩展配置并启用本机支持时使用该命令，也可以使用docker实例：

    
    
    docker pull lightbulb/lightbulb-framework

##
![LightBulb：一个用于审计web应用程序防火墙的开源框架541.png](https://image.3001.net/images/20190131/1548905965_5c526ded471a7.png!small)

## 安装 **Burp Extension**

如果你想使用新的GUI，可以使用Burp Suite的扩展程序。首先，你必须使用Burp Proxy和Jython设置工作环境

> 从[此处下载](http://www.jython.org/downloads.html)最新的Jython
>
> 找到你本地的python包安装文件夹*
>
> 配置Burp Extender以使用这些值，如下所示*

![lightbulb-framework_4.png](https://image.3001.net/images/20190131/1548905998_5c526e0ef3d1b.png!small)选择新的LightBulb模块（“BurpExtension.py”）并将扩展类型设置为“Python”

![lightbulb-framework_5.png](https://image.3001.net/images/20190131/1548906035_5c526e3344611.png!small)

*你也可以忽略此步骤，直接下载安装[包含所有所需python包的独立版本](https://github.com/lightbulb-framework/lightbulb-framework/files/2079793/lightbulb-framework.zip)。

##  **示例**

[Wiki page](https://github.com/lightbulb-framework/lightbulb-framework/wiki)的使用示例。

## 项目贡献人员

> George Argyros
>
> Ioannis Stais
>
> Suman Jana
>
> Angelos D. Keromytis
>
> Aggelos Kiayias

 ***参考来源：[kitploit](https://www.kitploit.com/2018/12/lightbulb-framework-tools-for-auditing.html)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

