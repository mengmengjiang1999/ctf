***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 一、事件背景

 **最近接到应急响应客户被勒索病毒攻击，深信服EDR安全团队捕获到相应的恶意样本，经分析确认此样本为Scarab勒索病毒变种样本。**

Scarab勒索病毒是利用Necurs僵尸网络进行传播，Necurs是世界上最大的僵尸网络之一，曾用于传播多个恶意家族样本，最新变种主要通过RDP爆破+人工植入的方式传播感染主机。

爆破的相关日志，如下：

![图片.png](https://image.3001.net/images/20180614/15289397413193.png!small)

## 二、样本分析

(1)样本通过GetKeyboardType获取当前用户键盘类型，如下：

![图片.png](https://image.3001.net/images/20180614/15289397464558.png!small)

(2)进行一连串的字符串解密操作，得到程序的一些加密配置信息等，如下：

![图片.png](https://image.3001.net/images/20180614/15289397498480.png!small)

(3)打开注册表项HKEY_CURRENT_USER\Software\ILRTISo，如下：

![图片.png](https://image.3001.net/images/20180614/1528939753117.png!small)

查询idle注册表项，是否设置，如下：

![图片.png](https://image.3001.net/images/20180614/15289397578351.png!small)

(4)拷贝自身到%APPDATA%\Roaming目录下，并重命名为sevnz.exe，如下：

![图片.png](https://image.3001.net/images/20180614/15289397612126.png!small)

通过CreateProcess调用cmd.exe命名执行：

/c copy /y [Virus文件名路径] %APPDATA%\sevnz.exe，如下：

![图片.png](https://image.3001.net/images/20180614/15289397669464.png!small)

病毒母体拷贝自身到%APPDATA%目录下sevnz.exe，如下：

![图片.png](https://image.3001.net/images/20180614/15289397725531.png!small)

(5)查询%APPDATA%目录下是否存在sevnz.exe程序，如下：

![图片.png](https://image.3001.net/images/20180614/15289397759052.png!small)

然后自己传入参数“runas”,并调用ShellExecuteW生成一个新的进程，如下：

![图片.png](https://image.3001.net/images/20180614/15289397796224.png!small)

(6)执行%APPDATA%目录下的sevnz.exe程序，如下：

![图片.png](https://image.3001.net/images/20180614/1528939783461.png!small)

(7)sevnz.exe通过CreateProcess调用cmd.exe命名执行：

    
    
    mshta.exe javascript:o=newActiveXObject(‘Scripting.FileSystemObject’);setInterval(function(){try{o.DeleteFile(‘[FileName.exe]’);close()}catch(e){}},10);

删除母体文件，动态调试，如下：

![图片.png](https://image.3001.net/images/20180614/15289397893911.png!small)

(8)母体样本通过删除sevnz.exe，来判断之前的sevnz.exe是否启动，如下：

![图片.png](https://image.3001.net/images/20180614/15289397931031.png!small)

如果程序已启动，删除会失败，如下：

![图片.png](https://image.3001.net/images/20180614/15289398411297.png!small)

(9)当sevnz.exe在运行之中时，调用JavaScript脚本，将此进程添加到注册表的auto-run，相应的脚本命令：

    
    
    mshta.exe“javascript:o=new ActiveXObject(‘WScript.Shell’);
    
    x=newActiveXObject(‘Scripting.FileSystemObject’);
    
    setInterval(function(){try{i=x.GetFile(‘sevnz.exe’).Path;
    
    o.RegWrite(‘HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce\\ILRTISo’,i);}
    
    catch(e){}},10);

动态调试跟踪，如下：

![图片.png](https://image.3001.net/images/20180614/15289398497703.png!small)

自启动项创建完成之后，如下：

![图片.png](https://image.3001.net/images/20180614/15289398534385.png!small)

(10)创建加密线程，执行勒索病毒的主要加密流程，如下：

![图片.png](https://image.3001.net/images/20180614/15289398568278.png!small)

(11)通过JavaScript脚本读取注册表项HKEY_CURRENT_USER\Software\JBGUJ中的键值，然后执行里面的命令，如下：

![图片.png](https://image.3001.net/images/20180614/15289398591544.png!small)

注册表项中相关的命令脚本如下：

    
    
    o=new ActiveXObject("WScript.Shell");
    
    o.Run("cmd.exe /c wbadmin DELETE SYSTEMSTATEBACKUP -keepVersions:0",0);
    
    o.Run("cmd.exe /c wmic SHADOWCOPY DELETE",0);
    
    o.Run("cmd.exe /c vssadmin Delete Shadows /All /Quiet",0);
    
    o.Run("cmd.exe /c bcdedit /set {default} recoveryenabled No",0);
    
    o.Run("cmd.exe /c bcdedit /set {default} bootstatuspolicy ignoreallfailures",0);

通过上面的脚本命令，删除磁盘卷影文件，防止用户恢复文件

(12)启动线程，执行加密流程，如下：

![图片.png](https://image.3001.net/images/20180614/15289398644989.png!small)

(13)遍历主机进程列表，发现如下进程列表，则结束，相关的进程列表如下：

    
    
    agntsvc.exe;isqlplussvc.exe;ncsvc.exe;msftesql.exe;sqlagent.exe;sqlbrowser.exe;sqlservr.exe;sqlserver.exe;sqlwriter.exe;oracle.exe;ocssd.exe;dbsnmp.exe;synctime.exe;mydesktopqos.exe;agntsvc.exeisqlplussvc.exe;xfssvccon.exe;mydesktopservice.exe;ocautoupds.exe;agntsvc.exeagntsvc.exe;agntsvc.exeencsvc.exe;firefoxconfig.exe;tbirdconfig.exe;ocomm.exe;mysqld.exe;mysqld-nt.exe;mysqld-opt.exe;dbeng50.exe;sqbcoreservice.exe;

动态调试，得到相关的进程列表如下：

![图片.png](https://image.3001.net/images/20180614/15289398685644.png!small)

结束进程的代码如下：

![图片.png](https://image.3001.net/images/20180614/15289398716050.png!small)

(14)加密文件的主函数过程代码，如下：

![图片.png](https://image.3001.net/images/20180614/15289398745105.png!small)

![图片.png](https://image.3001.net/images/20180614/15289398775467.png!small)

(15)删除HKEY_CURRENT_USER\Software\JBGUJ注册表项的内容，如下：

![图片.png](https://image.3001.net/images/20180614/15289398815673.png!small)

(16)加密流程执行完成之后，原文件变为了scarab后缀的文件，如下：

![图片.png](https://image.3001.net/images/20180614/15289398847222.png!small)

同时弹出相关的勒索信息，如下：

![图片.png](https://image.3001.net/images/20180614/15289398874065.png!small)

## 三、预防措施

同时深信服EDR安全团队提醒用户：

> 1.不要点击来源不明的邮件以及附件
>
> 2.及时给电脑打补丁，修复漏洞
>
> 3.不从垃圾网站或不明网站下载软件
>
> 4.安装专业的终端/服务器安全防护软件
>
> 5.此勒索病毒变种主要通过RDP爆破的方式，建议用户及时修改密码

## 四、相关IOC

 **MD5**

9A02862AC95345359DFC3DCC93E3C10E

 *** 本文作者：千里目安全实验室，转载注明来自FreeBuf.COM**  

