**今天给大家介绍的是一款名叫R3con1z3r的轻量级Web信息收集工具，该工具采用Python开发，功能强大但使用简单。它提供了一个功能强大的基于开源情报（OSINT）指纹的数据收集环境，并可以进行快速且完整的信息收集任务。**

![1.png](https://image.3001.net/images/20181228/1545988016_5c25e7b06f6e9.png!small)

## R3CON1Z3R

在一次渗透测试中，信息指纹收集是第一个阶段的工作，此时需要尽可能地收集完整的目标信息。R3con1z3r是一款内置了多种功能的被动型网络侦查工具，其中包括：HTTP头标记、Traceroute、Whois指纹、DNS信息、服务器托管的站点、Nmap端口扫描、反向扫描网页中的对象以及超链接。该工具在获取到必要的基本输入信息之后，能够将数据收集报告以HTML格式输出。

### 工具截图

![2.png](https://image.3001.net/images/20181228/1545988023_5c25e7b75e768.png!small)![3.png](https://image.3001.net/images/20181228/1545988023_5c25e7b78a317.png!small)

## 工具安装

r3con1z3r支持Python 2和Python 3，安装命令如下：

    
    
    $ git clone <https://github.com/abdulgaphy/r3con1z3r.git>
    
    $ cd r3con1z3r
    
    $ pip install -r requirements.txt

### Linux用户可选项：

    
    
    $sudo chmod +x r3con1z3r.py

### 模块

r3con1z3r仅需要系统库和一些基础的Python模块。

Python3：

    
    
    $pip3 install -r requirements.txt

Windows：

    
    
    pip installwin_unicode_console colorama

## 工具使用

    
    
    python3 r3con1z3r.py [domain.com]

## 使用样例

在所有操作系统环境（Linux、Windows、macOS和Android等）下使用Python 2：

    
    
    python r3con1z3r.py google.com

在Python 3环境下运行：

    
    
    python3 r3con1z3r.py facebook.com

Unix以可执行文件运行：

    
    
    ./r3con1z3r.py google.com

## 许可证协议

r3con1z3r遵循[GNU
GPL许可证协议](https://github.com/abdulgaphy/r3con1z3r/blob/master/LICENSE)开发。

***参考来源：[r3con1z3r](https://github.com/abdulgaphy/r3con1z3r)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

