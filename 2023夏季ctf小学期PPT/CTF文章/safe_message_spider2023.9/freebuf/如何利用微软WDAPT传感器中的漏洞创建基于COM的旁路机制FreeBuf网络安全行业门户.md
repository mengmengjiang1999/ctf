![](https://image.3001.net/images/20210609/1623225232_60c073904e3d39c683874.png!small)

## 关于Dent

Dent是一个可以创建基于COM的旁路机制的框架，该框架所生成的代码可以利用“Windows
Defender高级威胁保护”(WDATP)的ASR规则中的安全漏洞来执行Shellcode，而不被检测到或屏蔽掉。在Windows系统中，ASR被设计成第一道防线，可以根据规则来检测一系列违反规则的行为或事件。这些规则侧重于端点上的特定行为指标，这些指标通常与攻击者的战术、技术或过程（TTP）相关。这些规则侧重于微软Office套件，因为这是一种在端点上建立远程攻击点的通用攻击向量。

许多基于规则的控制都集中在基于网络或基于流进程的行为指标上，这些指标比正常的业务操作要更好识别。而这些规则主要关注系统的初始危害或可能严重影响组织的技术，比如凭证泄露或勒索软件攻击等等。它们涵盖了大量常见的攻击面，并侧重于阻止用于危害资产的已知技术。

Dent可以利用几个漏洞绕过这些限制控制策略，并在目标终端上执行Payload而不被Windows
Defender高级威胁保护WDATP传感器屏蔽或检测到。

## 工具安装

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/optiv/Dent.git

接下来，使用下列命令构建项目代码：

    
    
    go build Dent.go

## 帮助信息

    
    
    ./Dent -h
    
     
    
    ________                 __   
    
    \______ \   ____   _____/  |_
    
     |    |  \_/ __ \ /    \   __\
    
     |    |   \  ___/|   |  \  |  
    
    /_______  /\___  >___|  /__|  
    
            \/     \/     \/      
    
                    (@Tyl0us)
    
     
    
    "Call someone a hero long enough, and they'll believe it. They'll become it.
    
    They have no choice. Let them call you a monster, and you become a monster."
    
     
    
     
    
    Usage of ./Dent:
    
      -C string
    
            Name of the COM object.
    
      -N string
    
            Name of the XLL playload when it's writen to disk.
    
      -O string
    
            Name of the output file. (default "output.txt")
    
      -P string
    
            Path of the DLL for your COM object. (Either use \\ or '' around the path)
    
      -U string
    
            URL where the base64 encoded XLL payload is hosted.
    
      -show
    
            Display the script in the terminal.

## 武器化开发

此框架旨在利用Microsoft Defender Advanced Threat
Protection中的漏洞和不足，因为它实际上不会生成任何的Payload。为了生成Payload，我们可以使用其他的一些工具，本框架所有的Payload和其他组件都是基于[
_ScareCrow_](https://github.com/optiv/ScareCrow)生成和实现的。

### ScareCrow武器化-伪造COM对象模式

如需使用一个ScareCrow Payload并执行绕过的话，可以使用下列命令：

    
    
    ./ScareCrow -I <path to your raw stageless shellcode>  -domain <domain name> -Loader dll

ScareCrow武器化-远程.XLL Payload模式

如需使用一个ScareCrow Payload并执行绕过的话，可以使用下列命令：

    
    
    ./ScareCrow -I <path to your raw stageless shellcode>  -domain <domain name> -Loader dll

生成之后，从输出文件中复制第13和第14行，混合之后，确保移除下列内容：

> var <variable name>
>
> 每一行结尾的“;”符号
>
> 每个字符串前后的引号

![](https://image.3001.net/images/20210609/1623225282_60c073c24b6775d3c268c.png!small)

## 项目地址

Dent：【[ _GitHub传送门_](https://github.com/optiv/Dent)】

## 参考资料

> [ _https://www.optiv.com/insights/source-zero/blog/breaking-wdapt-rules-> com_](https://www.optiv.com/insights/source-zero/blog/breaking-wdapt-rules-> com)
>
> [ _https://github.com/optiv/ScareCrow﻿_](https://github.com/optiv/ScareCrow)

