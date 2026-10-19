**项目地址：https://github.com/chroblert/JCTokenUtil**

 **version3版本**

 ***本工具仅供技术分享、交流讨论，严禁用于非法用途。**

##  **0x01** **前言**

在上篇文章[研究|Windows访问令牌原理与实践(一)](http://mp.weixin.qq.com/s?__biz=MzAxNTcyNTY1NQ==&mid=2648060702&idx=1&sn=b879df8693b403084f0f0bd4a88f0df6&chksm=83dd3626b4aabf301e999cb1315bc09d2c80767145ff219738a6d6b062972511496cbbe0531b&scene=21#wechat_redirect)中说到了一些原理方面的内容，也有使用incognito工具进行了一些验证但，也还是存在一些不足。

比如：通过运行win+R访问共享文件夹时，使用incognito工具是查不到所输入的用户的token的。

![1621763303_60aa24e7b7d3eb31bac0b.png!small](https://image.3001.net/images/20210523/1621763303_60aa24e7b7d3eb31bac0b.png!small)

如下左图使用incognito工具没有看到test用户，右图我改写的工具成功的列出了所使用的test用户。

![1621763314_60aa24f2751dcc16e6628.png!small](https://image.3001.net/images/20210523/1621763314_60aa24f2751dcc16e6628.png!small)

##  **0** **x02** **介绍**

本工具参考incognito的代码进行编写，完成了 **获取token** 和 **以某token执行命令** 两个功能。

在获取系统上所有token的时候， **incognito工具**
使用NtQuerySystemInformation微软未公开API获取系统上所有的进程，然后再获取该进程上句柄表中的每一个句柄，判断是不是token句柄，若是则保存。

 **JCTokenUtils** **工具**
同样使用NtQuerySystemInformation微软未公开API，不过是直接获取系统上所有的句柄，之后判断是不是token句柄，若是则保存。由于句柄表中没有保存进程自身的主令牌，因而会使用OpenProcessTokenAPI获取并保存进程的主令牌。

以某个令牌执行命令，本工具基本参照incognito工具编写，没有区别。

##  **0** **x03** **使用**

###  **0** **x0301** **命令介绍**

    
    
    Usage: TokenUtil.exe <module> [OPTION]  
      
    [MODULE]  
    ListTokens  
    [OPTION]  
    -p <pid>: 列出某个进程中的令牌  
    -P <procName>: 列出某个进程的令牌  
    -u <username>: 列出某个用户的令牌  
    -v : 详细模式 // 不加-v，每个用户只输出一次  
      
    example:  
    TokenUtils.exe ListTokens -u "NT AUTHORITY\SYSTEM"  
    TokenUtils.exe ListTokens -P "cmd"  
    TokenUtils.exe ListTokens -P "cmd" -u "NT AUTHORITY\SYSTEM"  
      
    [MODULE]  
    Execute  
    [OPTION]  
    -p <pid>: 以指定pid的token执行命令  
    -u <username>: 以某个用户执行命令，与-e <command>结合使用  
    -e <command> : 执行命令  
    -c: 是否在当前终端下执行  
    -v : 详细模式  
      
    example:  
    TokenUtils.exe Execute -p <pid> -e whoami -c  
    TokenUtils.exe Execute -u "NT AUTHORITY\SYSTEM" -e whoami -c  
    TokenUtils.exe Execute -p <pid> -u "NT AUTHORITY\SYSTEM" -e whoami -c

###  **0** **x0302** **使用说明**

· -P -u参数值大小写敏感

· 同时使用-P -u参数表示同时满足两个条件

· 获取token时同一个用户只输出一次，使用-v参数，则输出所有用户

###  **0** **x0303** **使用效果**

![1621763600_60aa261093dd1b343b183.png!small](https://image.3001.net/images/20210523/1621763600_60aa261093dd1b343b183.png!small)

    
    
    TokenUtil.exe ListTokens -u jerrybird

![](https://image.3001.net/images/20210523/1621763203_60aa248309f384fc47430.png!small)

    
    
    TokenUtils.exe ListTokens -u jerrybird -v

![图片](https://image.3001.net/images/20210523/1621763228_60aa249c6c76529097cfd.png!small)

    
    
    TokenUtil.exe Execute -u"DESKTOP-UIK8D53\test" -e cmd -c

![图片](https://image.3001.net/images/20210523/1621763241_60aa24a9c50fc8c3c3594.png!small)

