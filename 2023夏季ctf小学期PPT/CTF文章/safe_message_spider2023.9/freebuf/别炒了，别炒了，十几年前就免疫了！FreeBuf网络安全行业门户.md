## **1 威胁概述**

2021年1月13日，江民赤豹网络安全实验室接到合作伙伴反馈网络上发现一款会删除磁盘文件的病毒。该病毒执行后会创建自身副本到系统盘Windows目录下，并创建注册表设置自启动，用户重启机器后，病毒自启动进程将会遍历除系统盘外的所有磁盘，并对文件进行删除。经过排查发现，江民各版本杀毒软件均可对该病毒进行查杀，目前暂未发现江民客户受该病毒影响。

病毒名：Worm/AutoRun.hwk（业界称为“incaseformat”病毒），早在2009年4月9日，江民病毒监测网就捕获了该样本，本次研究发现近期有大范围爆发趋势。

##  **2 代码分析**

江民最早于2009年4月9日捕获该病毒，该病毒为32位PE文件，为Delphi语言编写，通过U盘传播。

![1611303599_600a8aafaca87dbac1722.png!small](https://image.3001.net/images/20210122/1611303599_600a8aafaca87dbac1722.png!small)

该病毒的图标跟windows xp默认的文件夹图标是一样的，很具有迷惑性。病毒运行后首先复制自身到C:\windows\tsay.exe。

然后创建注册表值，将自身副本程序设置为开机自启：

注册表：

HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce\msfsa

值: C:\windows\tsay.exe。

C:\windows\tsay.exe文件会在重启后运行，将自身拷贝到C:\windows\ttry.exe。然后在非系统盘符下，创建与文件夹同名的可执行文件。接着设置以下注册表，来隐藏文件：

HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced\HideFileExt
0x00000001

HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced\Hidden
0x00000002

HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced\Folder\Hidden\SHOWALL\checkedvalue
0x00000000

根据时间来判断，执行伪装文件的操作，还是执行删除文件的操作。由于时间换算的错误，导致该病毒潜藏到2021年1月13日才爆发，并且错误的执行了删除文件的操作。

![1611303623_600a8ac78e772e21ac7a1.png!small](https://image.3001.net/images/20210122/1611303623_600a8ac78e772e21ac7a1.png!small)

图 根据时间判断执行操作

![1611303647_600a8adf7de41ed3eafba.png!small](https://image.3001.net/images/20210122/1611303647_600a8adf7de41ed3eafba.png!small)

图 时间判断

最后删除非系统分区下所有文件，在每个盘符下都产生一个大小为0kb、文件名为incaseformat的文本文档。

总结：该病毒原版是伪装成文件夹，隐藏原文件夹，以此来隐藏自身、通过U盘传播。由于时间戳判断错误，不再进行隐藏，而是执行删除操作。

  

## 3 危害级别

该病毒会恶意删除用户磁盘文件，对用户的计算机数据造成极大威胁。

## 4 处理方案

1、 结束进程C:\windows\ttry.exe

2、 删除文件C:\windows\tsay.exe、C:\windows\ttry.exe

3、
还原注册表，并将文件隐藏关闭。HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced\HideFileExt

HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced\Hidden

HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced\Folder\Hidden\SHOWALL\checked

4、 使用分区工具进行文件还原。

  

江民各版本杀软均可对该病毒进行查杀和防护。

![1611303799_600a8b7732213d52bb708.png!small](https://image.3001.net/images/20210122/1611303799_600a8b7732213d52bb708.png!small)

图1 江民网络版V19查杀截图

![1611303822_600a8b8e9811cf302b20f.png!small](https://image.3001.net/images/20210122/1611303822_600a8b8e9811cf302b20f.png!small)

图2 江民网络版V16查杀截图

![1611303842_600a8ba2dc8e2b71ec8b3.png!small](https://image.3001.net/images/20210122/1611303842_600a8ba2dc8e2b71ec8b3.png!small)

图3 江民速智版查杀截图

