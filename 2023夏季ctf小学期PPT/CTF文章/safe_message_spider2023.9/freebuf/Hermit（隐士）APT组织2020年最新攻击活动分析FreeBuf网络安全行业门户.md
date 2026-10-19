## 一、概述

**两年前，腾讯安全威胁情报中心曝光了SYSCON/SANNY木马的活动情况，并且根据关联分析确定跟KONNI为同一组织所为。该组织的攻击对象包括与朝鲜半岛相关的非政府组织、政府部门、贸易公司、新闻媒体等。**

SYSCON/SANNY木马是一个非常有特色的远程控制木马，通过ftp协议来进行C&C控制，该后门的主要攻击目标为朝鲜半岛相关的重要政治人物或者要害部门，偶尔也会针对东南亚等国进行攻击。该活动自2017年下半年开始活跃，并且对多个目标进行了攻击活动。被曝光后，该组织活动没有任何减弱的迹象。腾讯安全威胁情报中心根据该组织的特点，在2018年12月将其命名为“Hermit（隐士）”。

2020年，“Hermit（隐士）”APT组织依然保持较高的活跃度，攻击方式和木马行为上也有了较大的更新，因此我们对近期的攻击活动做一个整理，并对木马的一些更新情况做一个详细分析汇总。

![](https://image.3001.net/images/20200426/1587865316_5ea4e6e481c3c.png!small)

## 二、诱饵

使用带有恶意Office宏代码的攻击诱饵依然是SYSCON/SANNY最常用的攻击方式，此外通过修改字体颜色来伪装宏代码的恶意行为也是该组织的特点之一，该特点一直保持至今。而诱饵的主题依然是紧贴时事热点，尤其是全球新冠疫情（COVID-19）热点以及朝鲜半岛相关的局部热点事件。

例如3月份“Hermit（隐士）”组织使用“口罩仅建议用于照顾COVID-19病人的人使用”的文档标题作为攻击诱饵。

![](https://image.3001.net/images/20200426/1587865325_5ea4e6ed0cc6e.png!small)

“Hermit（隐士）”使用新冠疫情（COVID-19）口罩话题为诱饵

![](https://image.3001.net/images/20200426/1587865333_5ea4e6f554618.png!small)

“Hermit（隐士）”组织使用2020年东京残奥会捐助相关的诱饵

![](https://image.3001.net/images/20200426/1587865341_5ea4e6fd82e62.png!small)

“Hermit（隐士）”组织伪装成2020年朝鲜政策相关话题为诱饵

![](https://image.3001.net/images/20200426/1587865348_5ea4e70451224.png!small)

“Hermit（隐士）”组织使用朝鲜Covid-19疫情相关主题为诱饵

## 二、恶意宏代码分析

携带恶意宏代码的恶意Office文件几乎是该组织的唯一攻击方式，多数诱饵会在未启用宏的情况下在诱饵文件中显示诱导内容，诱导用户启用宏，在未启用宏的情况下字体为几乎无法查看的灰色。

![](https://image.3001.net/images/20200426/1587865364_5ea4e71476b0e.png!small)

诱导受害者启用恶意宏代码查看文档

![](https://image.3001.net/images/20200426/1587865372_5ea4e71ccf5d1.png!small)

多数诱饵的vba宏代码使用密码保护

![](https://image.3001.net/images/20200426/1587865379_5ea4e72303069.png!small)

宏代码中会调整图片大小以及修改字体颜色，用来隐藏真实的恶意行为

最新的攻击宏代码主要恶意行为是释放一个PE文件，并创建进程执行，执行时会将配置的CC信息作为命令行参数传递给恶意进程。

![](https://image.3001.net/images/20200426/1587865387_5ea4e72bcd6d3.png!small)

释放PE文件相关宏代码之一

![](https://image.3001.net/images/20200426/1587865395_5ea4e733d9e1c.png!small)

释放PE文件相关宏代码之二

## 三、downloader&install过程分析

释放出的PE文件是一个downloader木马，其主要功能是从命令行参数中提取URL，并进行一系列的下载、解压和安装行为，以下以最新版本的文件up.exe（a83ca91c55e7af71ac4f712610646fca）作为样本进行详细分析。

up.exe行为：

1）首先从参数中取出URL，然后判断操作系统是32位还是64位，如果32位则下载2.dat、64位下载3.dat下载完成后将其解密成temp.cab，随后执行expand命令对cab进行解压释放

![](https://image.3001.net/images/20200426/1587865424_5ea4e75046d50.png!small)

downloader主要功能函数

2）cab内容如下，主要包含一个安装bat文件、一个RAT dll文件、一个ini文件

![](https://image.3001.net/images/20200426/1587865432_5ea4e7587bf1c.png!small)

cab压缩包内容

3）检查当前进程权限，不同权限不同处理方式

![](https://image.3001.net/images/20200426/1587865442_5ea4e76240d42.png!small)

进程权限检测相关代码

4）如果不是TokenElevationTypeLimited权限，即管理员用于以非管理员权限运行程序，则直接winexec执行install.bat，如果是TokenElevationTypeLimited则判断cmd.exe的版本，根据版本不同执行不同的UAC
bypass策略，共内置了三种绕过UAC的方式。

![](https://image.3001.net/images/20200426/1587865449_5ea4e769bfcce.png!small)

根据cmd版本信息使用不同的UAC bypass方案

5）UAC bypass方式一相关代码

![](https://image.3001.net/images/20200426/1587865457_5ea4e7715018f.png!small)

UAC bypass方式一

6）UACbypass方式二相关代码

![](https://image.3001.net/images/20200426/1587865466_5ea4e77a59a8d.png!small)

UAC bypass方式二

7）UAC bypass方式三相关代码

![](https://image.3001.net/images/20200426/1587865474_5ea4e782b196b.png!small)

UAC bypass方式三

8）install.bat的功能就是将wprint.dll和wprint.ini复制到system32目录，并创建服务持久化dll

![](https://image.3001.net/images/20200426/1587865482_5ea4e78a634e8.png!small)

install.bat

## 四、RAT行为详细分析

1，首先判断目录下是否有dll同名的dat文件，如果有则读取并解密出配置信息，如果没有则读取同名的ini文件，即wprint.ini并解密，解密得到URL后进行不断尝试下载dat

![](https://image.3001.net/images/20200426/1587865491_5ea4e7932f59c.png!small)

解密ini获取url下载dat相关代码

2、wprint.ini解密结果如下：是一个url，使用URLDownloadToFile进行下载后存为wprint.dat

![](https://image.3001.net/images/20200426/1587865499_5ea4e79bac6a7.png!small)

解密后的ini内容

3）读取wprint.dat并解密，得到包括ftpserver、username、password在内的配置信息

![](https://image.3001.net/images/20200426/1587865507_5ea4e7a307913.png!small)

从dat从提取配置信息相关代码

4）根据配置信息连接ftpserver，并将server上的htdocs设置为当前目录，在其中创建一个以本地computername加密后的字符串为名称的新目录

![](https://image.3001.net/images/20200426/1587865514_5ea4e7aa31f93.png!small)

连接ftpserver、创建目录相关代码

5）先后执行cmd /c systeminfo >temp.ini、cmd /c tasklist >
temp.ini两个命令收集计算机信息和进程列表，加密上传temp.ini文件到ftpserver并以ff mm-dd hh-mm-ss.txt的时间格式命名。

![](https://image.3001.net/images/20200426/1587865522_5ea4e7b2bcef1.png!small)

执行命令获取信息相关代码

6）ftp上传文件相关代码，除了.cab、.zip、.rar外的其他扩展名文件均会被压缩成.cab后加密上传

![](https://image.3001.net/images/20200426/1587865530_5ea4e7bab8cea.png!small)

上传信息、文件相关代码

7）依次下载ftpserver上的cc(x)文件到本地解析指令进行命令分发，x为从0开始依次自增的整数

![](https://image.3001.net/images/20200426/1587865537_5ea4e7c191e41.png!small)

获取控制指令相关代码

![](https://image.3001.net/images/20200426/1587865543_5ea4e7c7a273b.png!small)

获取控制指令相关代码

8）命令文件格式为开头“#”字符与第二个“#”之间的为下发的文件内容，第二个“#”之后的为指令内容

![](https://image.3001.net/images/20200426/1587865549_5ea4e7cdea61f.png!small)

解析控制文件cc相关代码

9）控制指令列表如下：主要完成cmdshell和文件上传下载执行的功能

指令参数1 指令参数2 指令参数3 功能 cmd /c 带pull 带/f 将目标文件复制到%temp%\temp.ini，上传temp.ini 不带/f
直接上传指定文件 带put 将下载的文件移动到指定位置 带> cmdshell 结果输出到temp.ini 不带> cmdshell /user
带/stext或> 使用user权限执行下载的文件，输出结果到temp.ini 不带/stext或> 使用user权限执行下载的文件 带/stext
执行下载的文件输出结果到temp.ini 不带/stext 执行下载的文件

**指令参数1** | **指令参数2** | **指令参数3** | **功能**  
---|---|---|---  
cmd /c | 带pull | 带/f | 将目标文件复制到%temp%\temp.ini，上传temp.ini  
不带/f | 直接上传指定文件  
带put |  
| 将下载的文件移动到指定位置  
  
| 带> | cmdshell 结果输出到temp.ini  
不带> | cmdshell  
/user | 带/stext或> | 使用user权限执行下载的文件，输出结果到temp.ini  
不带/stext或> | 使用user权限执行下载的文件  
  
| 带/stext | 执行下载的文件输出结果到temp.ini  
不带/stext | 执行下载的文件  
  
命令参数表

10）cmd /c指令相关处理代码如下

![](https://image.3001.net/images/20200426/1587865560_5ea4e7d81c394.png!small)

cmd命令相关代码

11）/user指令相关处理代码如下

![](https://image.3001.net/images/20200426/1587865567_5ea4e7df9122e.png!small)

user命令相关代码

12）其他指令处理代码如下

![](https://image.3001.net/images/20200426/1587865574_5ea4e7e64e46f.png!small)

其他命令相关处理代码

## 四、版本变化

SYSCON/SANNY的活动最早可追溯到2017年，使用ftp协议作为RAT控制协议的木马是该组织最早使用也是最长使用的手法，与之前版本的木马相比，近期攻击所使用的木马有以下升级点：

**** | **老版本** | **新版本**  
---|---|---  
下载解密 | 利用系统组件certutil.exe进行下载解密 | 自己编写的downloader和解密代码  
UAC bypass | 一个专门的dll中一种bypass方法 | 集成在downloader中，三种bypass方法  
加解密 | 文件名字符串、CC传输文件未加密 | 对包括所有字符串、与CC传输的文件都加密了  
控制文件 | everyone(0) | cc(0)  
RAT指令 | 有对chip控制指令的处理 | 没有对chip控制指令的处理  
  
## 五、附录IOC

### HASH

> guidance.doc：
>
> 677e200c602b44dc0a6cc5f685f78413
>
> 123.doc：
>
> 40e7a1f37950277b115d5944b53eaf3c
>
> Keepan eye on North Korean cyber.doc：
>
> 1a7232ef1386f78e76052827d8f703ae
>
> KinzlerFoundation for 2020 Tokyo Paralympic games.doc:
>
> faf6492129eeca2633a68c9b8c2b8156
>
> ce26d4e20d936ebdad92f29f03dfc1d9
>
> 7e71d5a0f1899212cea498bbda476ce8
>
> a83ca91c55e7af71ac4f712610646fca
>
> 77f46253fd4ce7176df5db8f71585368
>
> 62e959528ae9280f39d49ba5c559d8fb

### C2

> phpview.mygamesonline.org
>
> firefox-plug.c1.biz
>
> win10-ms.c1.biz
>
> ftpserver:myview-202001.c1.biz
>
> username:3207035
>
> password:1qazXSW@3edc

## 六、相关链接

> <https://mp.weixin.qq.com/s/rh4DoswLUNkS8uiHjrFU9A>
>
> <https://mp.weixin.qq.com/s/CBh2f-lfG5H4wcoj5VSfEw>
>
> <https://mp.weixin.qq.com/s/F2-DLtuHUkV_nCnKwp44_Q>

*本文作者：腾讯电脑管家，转载请注明来自FreeBuf.COM

