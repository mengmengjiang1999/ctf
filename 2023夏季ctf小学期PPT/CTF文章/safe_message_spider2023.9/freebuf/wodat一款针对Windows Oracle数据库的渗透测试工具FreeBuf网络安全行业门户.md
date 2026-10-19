![](https://image.3001.net/images/20221125/1669367531_638086ebb2d3fc983026d.png!small)

## 关于wodat

wodat是一款功能强大的针对Windows Oracle数据库的渗透测试工具，该工具基于C# .Net
Framework开发，能够帮助广大研究人员对Windows平台下的Oracle数据库执行按摩全渗透测试任务。

注意：请在被授权执行安全测试的情况下使用该工具。

![](https://image.3001.net/images/20221125/1669367541_638086f52da367f165de0.png!small)

## 功能介绍

> 1、执行基于密码的渗透测试，例如用户名、密码、用户名列表和用户名:密码组合等；
>
> 2、测试一个凭证或链接字符串对目标是否有效；
>
> 3、执行暴力破解任务以发现有效的SID/ServiceName;
>
> 4、使用提供的目标文件或CIDR范围扫描有效的TNS监听器；
>
> 5、其他功能...

## 工具下载&安装

广大研究人员可以使用下列命令将该项目下载到本地：

    
    
    git clone https://github.com/InitRoot/wodat.git

接下来，切换到项目目录下并使用下列命令自行构建项目代码：

    
    
    nuget restore wodat.sln
    
    msbuild wodat.sln -t:rebuild -property:Configuration=Release

## 工具使用

下面给出的是该工具的常用命令行参数选项：

    
    
    wodat.exe COMMAND ARGGUMENTS
    
     COMMAND (ALL,BRUTECRED,BRUTESID,BRUTESRV,TEST,DISC)
    
     -server:XXX.XXX.XXX.XXX -port:1520
    
     -sid:AS OR -srv:AS
    
     -user:Peter -pass:Password

测试一个指定的凭证集是否有效：

    
    
    wodat.exe TEST -server:XXX.XXX.XXX.XXX -port:1521 -sid:XE -user:peter -pass:pan

## 功能模块

### BRUTESID模块（SID爆破）

wodat提供的BRUTESID模块可以针对SID执行字典猜解攻击，如果失败的话，则会询问是否执行暴力破解攻击：

    
    
    wodat.exe BRUTESID -server:XXX.XXX.XXX.XXX -port:1521

![](https://image.3001.net/images/20221125/1669367661_6380876d7250fd577f353.png!small)

### BRUTESRV模块（Service爆破）

wodat提供的BRUTESRV模块可以针对ServiceName执行字典猜解攻击，如果失败的话，则会询问是否执行暴力破解攻击：

    
    
    wodat.exe BRUTESRV -server:XXX.XXX.XXX.XXX -port:1521

### BRUTECRED模块（凭证爆破）

wodat提供的BRUTECRED模块可以执行基于字典密码的攻击测试，并提供下列参数选项：

A - 用户名:密码组合列表

B - 用户名列表

C - 密码列表

D - 用户名作为密码

下列命令可以根据给定的包含“用户名:密码”组合的文件执行猜解攻击：

    
    
    wodat.exe BRUTECRED -server:XXX.XXX.XXX.XXX -port:1521 -sid:XE

![](https://image.3001.net/images/20221125/1669367674_6380877a6b493daf3aff2.png!small)

### 测试模块

该模块用于测试给定的链接字符串是否有效：

    
    
    wodat.exe TEST -server:XXX.XXX.XXX.XXX -port:1521 -sid:XE -user:peter -pass:pan

![](https://image.3001.net/images/20221125/1669367680_63808780d263abb017787.png!small)

### DISC模块

该模块可以针对给定的CIDR范围或包含了实例的文件执行扫描。注意，只有带有有效TNS监听器的实例才会被返回，并且整个过程以并行方式进行，因此速度非常快：

    
    
    wodat.exe DISC

测试实例的格式必须以下列形式提供（targets.txt）：

    
    
    192.168.10.1
    
    192.168.10.5,1521

![](https://image.3001.net/images/20221125/1669367687_63808787b7729c551132c.png!small)

## 项目地址

 **wodat** ：【[ _GitHub传送门_](https://github.com/InitRoot/wodat)】

## 参考资料

> [
> _https://github.com/quentinhardy/odat﻿_](https://github.com/quentinhardy/odat)

